#####  Python essentials #####
import numpy as np
import glob
from tqdm import tqdm
import sys
import re
import math
import itertools
from pathlib import Path
import argparse
import time
import os.path
import pprint

sgn_dict = {'Ato4l': 1, 'hChToTauNu': 3, 'hToTauTau': 4, 'leptoquark': 5}
mode = 'ordered'

#################
#plotting

import matplotlib
from cycler import cycler
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
colors = []
for color in mcolors.TABLEAU_COLORS:
    colors.append(color)

custom_cycler = (cycler(marker=['o', '*', '+','v']) * cycler(color=colors) )
cc = []
for s in custom_cycler:
    cc.append(s)

################################################################################################################
################################################################################################################
import logging
# create logger
logger = logging.getLogger('svdd-plot-scores')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)



# def to_csv(modelname,Flags):
    
#     files_all = []
#     files = []

#     mode = Flags.mode

#     files_all = glob.glob('results/*/%s/*' % (modelname)) 
#     print(files_all)


#     files_sufix= [] 
#     for fname in tqdm(files_all):      
#       suffix = fname.split('/')[-1]
#       suffix = suffix.split('.txt')[0]
#       suffix = suffix.split('_')[2:]
#       files_sufix.append('_'.join(suffix))
    



#     f = open('results/csv/%s/scores.csv' % (modelname), 'w')
#     writer = csv.writer(f, delimiter=',')
#     writer.writerow(['Signal','Channel','Model','AUC','1e-2','1e-3','1e-4','1e-5']) 
#     counter = 0
#     files_sufix = list(set(files_sufix))
#     for fname in tqdm(files_sufix):
#       suffix = fname.split('_')
#       if mode == 'ordered':
#        suffix.remove('ordered')

#       if len(suffix) == 10:
#        channel = '_'.join(suffix[:4])
#        name = '_'.join(suffix[4:])
#       elif len(suffix) == 9:
#        channel = '_'.join(suffix[:3])
#        name = '_'.join(suffix[3:])
#       elif len(suffix) == 8:
#        channel = '_'.join(suffix[:2])
#        name = '_'.join(suffix[2:])
#       elif len(suffix) == 7:
#        channel = '_'.join(suffix[:1])
#        name = '_'.join(suffix[1:])
#       else:
#        continue

#       fp = open('results/metrics/AUC_SVDD_' + fname + '.txt', 'r')
#       lines = fp.read().splitlines()
#       auc = [float(i) for i in lines]
#       fp = open('results/metrics/Epsilon1_SVDD_' + fname + '.txt', 'r')
#       lines = fp.read().splitlines()
#       epsilon1 = [float(i) for i in lines]
#       fp = open('results/metrics/Epsilon2_SVDD_' + fname + '.txt', 'r')
#       lines = fp.read().splitlines()
#       epsilon2 = [float(i) for i in lines]
#       fp = open('results/metrics/Epsilon3_SVDD_' + fname + '.txt', 'r')
#       lines = fp.read().splitlines()
#       epsilon3 = [float(i) for i in lines]
#       fp = open('results/metrics/Epsilon4_SVDD_' + fname + '.txt', 'r')
#       lines = fp.read().splitlines()
#       epsilon4 = [float(i) for i in lines]

#       for i in range(len(xcoord)):
#          writer.writerow([xcoord[i], channel, name, auc[i], epsilon1[i], epsilon2[i], epsilon3[i], epsilon4[i]]) 

sgn_dict = {'Ato4l': 1,'SM': 2, 'hChToTauNu': 3, 'hToTauTau': 4, 'leptoquark': 5}
sgn_label_dict = {'Ato4l':r'$A \rightarrow 4l$','SM':r'$SM$', 'hChToTauNu':r'$h^{\pm} \rightarrow \tau \nu$','hToTauTau': r'$H(mass=60\: GeV) \rightarrow{} \tau\tau$','leptoquark': r'leptoquark(LQ,80 $mass = 80\:GeV) \rightarrow{} b \nu_{\tau}$ '}

# https://www.nature.com/articles/s41597-022-01187-8
# def plot(etype_training,regression,Flags):
#     print("INFO:: plotting data")
#     print("data shape")
#     print(print(regression))
#     print(regression.shape)
#     print(etype_training.shape)
#     outputdir = os.path.join(Flags.plotdir,"data")
#     if not os.path.exists(outputdir):
#         os.makedirs(outputdir)

#     plt.figure()
#     for icol in range(0,regression.shape[1]):
#         print(icol)
#         print(regression[:, icol])
#         column = regression[:, icol]
#         plt.yscale("log")
#         plt.hist(column, bins='auto')  # arguments are passed to np.histogram
#         plt.title("Histogram %s" % (icol ))
#         plt.savefig(os.path.join(outputdir,"%s.png"  % (icol )))
#         plt.clf()
#     plt.close()
#     return

def makeROCs(Flags):
    logger.info("in makeROCs")


    # if Flags.hls4ml:
    #     outputdir = os.path.join("figures","hls4ml_wrapper",Flags.modeldir,Flags.plotdir)
    # else:
    outputdir = os.path.join("figures",Flags.plotdir)

    print(outputdir)

    
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
        logger.info("made outputdir")
    plt.ion()
    plt.figure()
    logger.info("made figure")


    for i,key in enumerate(sgn_dict):
        # plt.plot([0,1],[0,1], 'k--')
        plt.yscale('log')
        plt.ylim([10E-4, 1.5])
        plt.xlim([0, 1.05])
        plt.grid(axis='x', color='0.95')
        plt.grid(axis='y', color='0.95')

        for k, model in enumerate(Flags.model):
            logger.info("plotting: %s" % model)
            logger.info("signal: %s" % key)


            # if Flags.hls4ml:
            #     outdirscores = os.path.join('results',Flags.modeldir,"hls4ml_wrapper",'scores',model,key)
            #     outdirROCs = os.path.join('results',Flags.modeldir,"hls4ml_wrapper",'ROCs',model,key)
            #     outdirsmetrics = os.path.join('results',Flags.modeldir,"hls4ml_wrapper",'metrics',model,key)
            # else:
            outdirscores = os.path.join('results',Flags.modeldir[k],'scores',model,key)

            outdirROCs = os.path.join('results',Flags.modeldir[k],'ROCs',model,key)

            outdirsmetrics = os.path.join('results',Flags.modeldir[k],'metrics',model,key)

            AUCdir = os.path.join('results',Flags.modeldir[k],'metrics',model,key)
            AUC = round(float(np.loadtxt(os.path.join(AUCdir,'AUC.txt'))),2)
            
            logger.info("loading %s" % (os.path.join(outdirROCs,'fpr.txt')))
            logger.info("loading %s" % (os.path.join(outdirROCs,'tpr.txt')))

            fpr = np.loadtxt(os.path.join(outdirROCs,'fpr.txt'))
            tpr = np.loadtxt(os.path.join(outdirROCs,'tpr.txt'))
            print(tpr)
            print(fpr)

            # roc_label = "SVDD ft %s zdim %s" % (model.split("_")[-2],model.split("_")[-1])
            # if 
            plt.plot( tpr,fpr, color = cc[k]["color"],linestyle="--", linewidth=2, label=Flags.labels[k] + ", AUC: %s" % str(AUC))


        plt.legend(loc="best")
        plt.title("ROC SVDD for Signal type %s" % (key ))

        plt.ylabel("Standard Model Background acceptance")
        plt.xlabel(r"%s Signal efficiency" % (sgn_label_dict[key]))


        logger.info("saving %s" % (os.path.join(outputdir,"%s_ROC.png" % (key))))

        plt.savefig(os.path.join(outputdir,"%s_ROC_log.png" % (key)))
        plt.yscale('linear')
        plt.ylim([-0.05, 1.05])
        plt.xlim([0, 1.05])
        plt.savefig(os.path.join(outputdir,"%s_ROC_lin.png" % (key)))
        plt.clf()

def makeAUC(Flags):
    logger.info("in makeAUC")

    plt.rcParams["figure.figsize"] = (10,6)
    # if Flags.hls4ml:
    #     outputdir = os.path.join("figures","hls4ml_wrapper",Flags.modeldir,Flags.plotdir)
    # else:
    outputdir = os.path.join("figures",Flags.plotdir)

    print(outputdir)
    print(Flags.modeldir)
    print(Flags.model)


    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
        logger.info("made outputdir")
    plt.ion()
    plt.figure()
    logger.info("made figure")


    for i,key in enumerate(sgn_dict):
        # plt.plot([0,1],[0,1], 'k--')
        plt.yscale('log')

        plt.grid(axis='x', color='0.95')
        plt.grid(axis='y', color='0.95')
        x = []
        y = []
        labels = []


        for k, model in enumerate(Flags.model):
            logger.info("plotting: %s" % model)
            logger.info("signal: %s" % key)


            AUCdir = os.path.join('results',Flags.modeldir[k],'metrics',model,key)
            if Flags.refmodeldir:
                refAUCdir = os.path.join('results',Flags.refmodeldir,'metrics',model,key)


            refAUC = np.loadtxt(os.path.join(refAUCdir,'AUC.txt'))
            AUC = np.loadtxt(os.path.join(AUCdir,'AUC.txt'))
            print(refAUC)
            print(AUC)
            print(Flags.labels[k])
            x.append(k+1)
            labels.append(Flags.labels[k])
            if Flags.refmodeldir:
                AUC = float(AUC)/float(refAUC)
                print(AUC)
            y.append(float(AUC))


        print(x,y)
        plt.plot( x,y, color = cc[k]["color"],linestyle="--", linewidth=2)
        plt.xticks(x, labels,rotation = -45)

        plt.legend(loc="best")
        plt.title("AUC %s" % (key ))

        plt.ylabel("AUC")
        plt.xlabel("Model parameters")


        logger.info("saving %s" % (os.path.join(outputdir,"%s_AUC.png" % (key))))

        plt.savefig(os.path.join(outputdir,"%s_AUC.png" % (key)))
        plt.yscale('linear')
        plt.ylim([-0.05, 1.05])

        plt.savefig(os.path.join(outputdir,"%s_AUC.png" % (key)))
        plt.clf()



def main(Flags):
    logger.info("in main")
    ModelNames = Flags.model
    print(ModelNames)

    if not os.path.exists('figures'):
        
        os.makedirs('figures')
        logger.info("made dir: figures")

    if len(Flags.modeldir) != len(Flags.model):
        print("give the same amount of models as modeldirs")
        logger.info("number of modeldirs %s" %(len(Flags.modeldir)) )

        return
    if len(Flags.labels) != len(Flags.model):
        print("give the same amount of models as labels")
        logger.info("number of labels %s" %(len(Flags.labels)) )
        return



    if Flags.make_roc_plots == 'True':
        makeROCs(Flags)
    if Flags.AUC == 'True':
        makeAUC(Flags)

    logger.info("Done")



if __name__ == '__main__':

    parser = argparse.ArgumentParser() 

    parser.add_argument('--mode', type=str, default='ordered', help='Type of encoding')

    parser.add_argument('--refmodel', type=str, default='False', help='Merge all the scores to a csv file for plotting')
    parser.add_argument('--refmodeldir', type=str, default='False', help='Merge all the scores to a csv file for plotting')

    parser.add_argument('--model', action='append', help='<Required> Set flag', required=True)

    parser.add_argument('--labels', action='append', help='<Required> Set flag', required=True)

    parser.add_argument('--plotdir', type=str, default="plots", help='plotdir')

    parser.add_argument('-d','--modeldir', action='append', help='<Required> Set flag', required=True)

    parser.add_argument('--convert_to_csv', type=str, default='True', help='Merge all the scores to a csv file for plotting')

    parser.add_argument('--AUC', type=str, default='False', help='Merge all the scores to a csv file for plotting')

    parser.add_argument('--make_box_plots', type=str, default='True', help='Make box and whisker plots')

    parser.add_argument('--make_roc_plots', type=str, default='False', help='Make box and whisker plots')

    parser.add_argument('--make_combination_plots', type=str, default='False', help='Make scores combinations plots')

    parser.add_argument('--make_random_combination_plots', type=str, default='False', help='Make scores random combinations plots')

    parser.add_argument('--n_comb', type=int, default=2, help='Number of combinations')   
    
    parser.add_argument('--hls4ml', type=bool, default=False, help='put quantised model in hls4ml wrapper')


    Flags, unparsed = parser.parse_known_args()
    main(Flags) 

    
         

    # if Flags.make_box_plots == 'True': 
    #     make_box_plots(Flags)

    # if Flags.make_combination_plots == 'True': 
    #     make_combined_plots(Flags)  

    # if Flags.make_random_combination_plots == 'True': 
    #     make_combined_rnd_plots(Flags)