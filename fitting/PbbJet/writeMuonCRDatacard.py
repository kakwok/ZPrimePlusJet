import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os
from hist import *  

from buildRhalphabetHbb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI,SF2017,SF2016,SF2018
from rhalphabet_builder import GetSF

def writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,options):
    obsRate = {}
    for box in boxes:
        obsRate[box] = histoDict['data_obs_%s'%box].Integral()
    nBkgd = len(bkgs)
    nSig = len(sigs)
    rootFileName = txtfileName.replace('.txt','.root')
    #rootFileName = txtfileName.replace('.txt','_hist.root')


    for key, myhist in histoDict.iteritems():
        if 'mcstat' in key:
            print 'mcstat names',key

    if options.year=='2018':
        BB_SF    =SF2018['BB_SF'] 
        BB_SF_ERR=SF2018['BB_SF_ERR']
        V_SF     =SF2018['V_SF']
        V_SF_ERR =SF2018['V_SF_ERR']
        LUMI_ERR = 1.025
    elif options.year=='2017':
        BB_SF    =SF2017['BB_SF'] 
        BB_SF_ERR=SF2017['BB_SF_ERR']
        V_SF     =SF2017['V_SF']
        V_SF_ERR =SF2017['V_SF_ERR']
        LUMI_ERR = 1.023
    elif options.year =='2016':
        BB_SF     =SF2016['BB_SF']
        BB_SF_ERR =SF2016['BB_SF_ERR']
        V_SF      =SF2016['V_SF']
        V_SF_ERR  =SF2016['V_SF_ERR']
        LUMI_ERR = 1.025


    rates = {}
    lumiErrs = {}
    hqq125ptErrs = {}
    mcStatErrs = {}
    veffErrs = {}
    bbeffErrs = {}
    znormEWErrs = {}
    znormQErrs = {}
    wznormEWErrs = {}
    mutriggerErrs = {}
    muidErrs = {}
    muisoErrs = {}
    jesErrs = {}
    jerErrs = {}
    puErrs = {}
    for proc in sigs+bkgs:
        for box in boxes:
            #print proc, box
            error = array.array('d',[0.0])
            rate = histoDict['%s_%s'%(proc,box)].IntegralAndError(1,histoDict['%s_%s'%(proc,box)].GetNbinsX(),error)
            rates['%s_%s'%(proc,box)]  = rate
            lumiErrs['%s_%s'%(proc,box)] = LUMI_ERR 
            #lumiErrs['%s_%s'%(proc,box)] = 1.025
            if proc=='hqq125':
                hqq125ptErrs['%s_%s'%(proc,box)] = 1.3                
            else:
                hqq125ptErrs['%s_%s'%(proc,box)] = 1.0
            if proc=='wqq' or proc=='zqq' or 'hqq' in proc:
                veffErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
                if box=='pass':
                    bbeffErrs['%s_%s'%(proc,box)] = 1.0+BB_SF_ERR/BB_SF
                else:
                    ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                    rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                    if rateFail>0:
                        bbeffErrs['%s_%s'%(proc,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    else:
                        bbeffErrs['%s_%s'%(proc,box)] = 1.0
                    
            else:
                veffErrs['%s_%s'%(proc,box)] = 1.
                bbeffErrs['%s_%s'%(proc,box)] = 1.
            mutriggerErrs['%s_%s'%(proc,box)] = 1
            muidErrs['%s_%s'%(proc,box)] = 1
            muisoErrs['%s_%s'%(proc,box)] = 1
            #jesErrs['%s_%s'%(proc,box)] = 1
            #jerErrs['%s_%s'%(proc,box)] = 1
            if proc=='wqq':
                wznormEWErrs['%s_%s'%(proc,box)] = 1.05
            else:
                wznormEWErrs['%s_%s'%(proc,box)] = 1.
            if proc=='zqq' or proc=='wqq':
                znormQErrs['%s_%s'%(proc,box)] = 1.1
                znormEWErrs['%s_%s'%(proc,box)] = 1.15
            else:
                znormQErrs['%s_%s'%(proc,box)] = 1.
                znormEWErrs['%s_%s'%(proc,box)] = 1.
                
            if options.noMcStatShape:                 
                if rate>0:
                    mcStatErrs['%s_%s'%(proc,box)] = 1.0+(error[0]/rate)
                else:
                    mcStatErrs['%s_%s'%(proc,box)] = 1.0
            else:
                for j in range(1,MASS_BINS+1):
                    mcStatErrs['%s_%s'%(proc,box),j] = 1.0
                
            if rate>0:
                rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral()
                rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral()
                rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral()
                rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral()
                ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral()
                ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral()
                jesErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                jerErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate)
                puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
            else:
                jesErrs['%s_%s'%(proc,box)] =  1.0
                jerErrs['%s_%s'%(proc,box)] =  1.0
                puErrs['%s_%s'%(proc,box)] =  1.0

    divider = '------------------------------------------------------------\n'
    datacard = 'imax 2 number of channels\n' + \
       'jmax * number of processes minus 1\n' + \
      'kmax * number of nuisance parameters\n' + \
      divider + \
      'bin fail_muonCR pass_muonCR\n' + \
      'observation %.3f %.3f\n'%(obsRate['fail'],obsRate['pass']) + \
      divider + \
      'shapes * pass_muonCR %s w_muonCR:$PROCESS_pass w_muonCR:$PROCESS_pass_$SYSTEMATIC\n'%rootFileName + \
      'shapes * fail_muonCR %s w_muonCR:$PROCESS_fail w_muonCR:$PROCESS_fail_$SYSTEMATIC\n'%rootFileName + \
      '#shapes * pass_muonCR %s $PROCESS_pass $PROCESS_pass_$SYSTEMATIC\n'%rootFileName + \
      '#shapes * fail_muonCR %s $PROCESS_fail $PROCESS_fail_$SYSTEMATIC\n'%rootFileName + \
      divider
    binString = 'bin'
    processString = 'process'
    processNumberString = 'process'
    rateString = 'rate'
    lumiString = 'lumi%s\tlnN'%options.suffix
    hqq125ptString = 'hqq125pt\tlnN'
    veffString = 'veff%s\tlnN'%options.suffix
    bbeffString = 'bbeff%s\tlnN'%options.suffix
    znormEWString = 'znormEW\tlnN'
    znormQString = 'znormQ\tlnN'    
    wznormEWString = 'wznormEW\tlnN'
    muidString = 'muid\tshape'   
    muisoString = 'muiso\tshape'   
    mutriggerString = 'mutrigger\tshape'  
    #jesString = 'JES\tshape'    
    #jerString = 'JER\tshape'
    jesString = 'JES%s\tlnN'%options.suffix
    jerString = 'JER%s\tlnN'%options.suffix
    puString = 'Pu%s\tlnN'%options.suffix
    mcStatErrString = {}
    for proc in sigs+bkgs:
        for box in boxes:
            if options.noMcStatShape:
                 mcStatErrString['%s_%s'%(proc,box)] = '%s%smuonCR%smcstat\tlnN'%(proc,box,options.year)
            else:
                for j in range(1,MASS_BINS+1):
                    mcStatErrString['%s_%s'%(proc,box),j] = '%s%smuonCR%smcstat%i\tshape'%(proc,box,options.year,j)

    for box in boxes:
        i = -1
        def format_string(number):
            if number==1:
                mystring = '\t-'
            else:
                mystring = '\t%.3f'%number
            return mystring         
        for proc in sigs+bkgs:
            i+=1
            if rates['%s_%s'%(proc,box)] <= 0.0: continue
            binString +='\t%s_muonCR'%box
            processString += '\t%s'%(proc)
            processNumberString += '\t%i'%(i-nSig+1)
            rateString += '\t%.3f' %rates['%s_%s'%(proc,box)]
            lumiString += format_string(lumiErrs['%s_%s'%(proc,box)])
            hqq125ptString += format_string(hqq125ptErrs['%s_%s'%(proc,box)])
            veffString += format_string(veffErrs['%s_%s'%(proc,box)])
            bbeffString += format_string(bbeffErrs['%s_%s'%(proc,box)])
            znormEWString += format_string(znormEWErrs['%s_%s'%(proc,box)])
            znormQString += format_string(znormQErrs['%s_%s'%(proc,box)])
            wznormEWString += format_string(wznormEWErrs['%s_%s'%(proc,box)])
            mutriggerString += '\t%.3f'%(mutriggerErrs['%s_%s'%(proc,box)])
            muidString += '\t%.3f'%(muidErrs['%s_%s'%(proc,box)])
            muisoString += '\t%.3f'%(muisoErrs['%s_%s'%(proc,box)])
            jesString += format_string(jesErrs['%s_%s'%(proc,box)])
            jerString += format_string(jerErrs['%s_%s'%(proc,box)])
            puString += format_string(puErrs['%s_%s'%(proc,box)])
            for proc1 in sigs+bkgs:
                for box1 in boxes:
                    if options.noMcStatShape:
                        if proc1==proc and box1==box:
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t%.3f'% mcStatErrs['%s_%s'%(proc,box)]
                        else:                        
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t-'
                    else:
                        for j in range(1,MASS_BINS+1):
                            if proc1==proc and box1==box:
                                mcStatErrString['%s_%s'%(proc1,box1),j] += '\t1.0'
                            else:                        
                                mcStatErrString['%s_%s'%(proc1,box1),j] += '\t-'

            
    binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n'; hqq125ptString+='\n';
    veffString+='\n'; bbeffString+='\n'; znormEWString+='\n'; znormQString+='\n'; wznormEWString+='\n'; mutriggerString+='\n'; muidString+='\n'; muisoString+='\n'; 
    jesString+='\n'; jerString+='\n'; puString+='\n';     
    for proc in (sigs+bkgs):
        for box in boxes:
            if options.noMcStatShape:                 
                mcStatErrString['%s_%s'%(proc,box)] += '\n'
            else:
                for j in range(1,MASS_BINS+1):
                    mcStatErrString['%s_%s'%(proc,box),j] += '\n'
            
    datacard+=binString+processString+processNumberString+rateString+divider

    # now nuisances
    datacard+=lumiString+hqq125ptString+veffString+bbeffString+znormEWString+znormQString+wznormEWString+mutriggerString+muidString+muisoString+jesString+jerString+puString

    # comment out total mcstat lnN errors
    for proc in (sigs+bkgs):
        for box in boxes:
            if rates['%s_%s'%(proc,box)] <= 0.0: continue
            if options.noMcStatShape:                 
                datacard+=mcStatErrString['%s_%s'%(proc,box)]
            else:
                for j in range(1,MASS_BINS+1):
                    error = histoDict['%s_%s'%(proc,box)].GetBinError(j)
                    rate  = histoDict['%s_%s'%(proc,box)].GetBinContent(j) 
                    if rate-error<=0:
                        print "rejecting %s_%s_%s"%(proc,box,j)
                        continue        ## veto small mcstat uncertainties
                    elif (error/rate)<=0.1 :
                        print "rejecting %s_%s_%s"%(proc,box,j)
                        continue        ## veto small mcstat uncertainties
                    else:
                        print "accepting %s_%s_%s with rate = %.5f, error = %.5f, error/rate = %.5f"%(proc,box,j,rate,error,error/rate)
                        datacard+=mcStatErrString['%s_%s'%(proc,box),j]
            

    # now top rate params
    tqqeff = histoDict['tqq_pass'].Integral()/(histoDict['tqq_pass'].Integral()+histoDict['tqq_fail'].Integral())

    
    datacard+='tqqpassmuonCR%snorm rateParam pass_muonCR tqq (@0*@1) tqqnormSF_%s,tqqeffSF_%s\n'%(options.year,options.year,options.year) + \
        'tqqfailmuonCR%snorm rateParam fail_muonCR tqq (@0*(1.0-@1*%.4f)/(1.0-%.4f)) tqqnormSF_%s,tqqeffSF_%s\n'%(options.year,tqqeff,tqqeff,options.year,options.year) + \
        'tqqnormSF_%s extArg 1.0 [0.0,10.0]\n'%options.year + \
        'tqqeffSF_%s extArg 1.0 [0.0,10.0]\n'%options.year
    
    #datacard+='* autoMCStats 0 0 1\n'
    txtfile = open(options.odir+'/'+txtfileName,'w')
    txtfile.write(datacard)
    txtfile.close()

    
def main(options, args):
    
    boxes = ['pass', 'fail']
    #for Hbb extraction:
    sigs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125']
    bkgs = ['zqq','wqq','qcd','tqq','vvqq','stqq','wlnu','zll']
    #for Wqq/Zbb extraction:
    #sigs = ['zqq','wqq']
    #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','vvqq','stqq','wlnu','zll']
    #for just Zbb extraction:
    #sigs = ['zqq']
    #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','wqq','vvqq','stqq','wlnu','zll']
    #systs = ['JER','JES','mutrigger','muid','muiso','Pu']
    systs = ['JER','JES','mutrigger','muid','muiso','Pu','mcstat']

    if options.year=='2018':
        BB_SF    =SF2018['BB_SF'] 
        BB_SF_ERR=SF2018['BB_SF_ERR']
        V_SF     =SF2018['V_SF']
        V_SF_ERR =SF2018['V_SF_ERR']
        sf_dict = SF2018
    elif options.year=='2017':
        BB_SF    =SF2017['BB_SF'] 
        BB_SF_ERR=SF2017['BB_SF_ERR']
        V_SF     =SF2017['V_SF']
        V_SF_ERR =SF2017['V_SF_ERR']
        sf_dict = SF2017
    elif options.year =='2016':
        BB_SF     =SF2016['BB_SF']
        BB_SF_ERR =SF2016['BB_SF_ERR']
        V_SF      =SF2016['V_SF']
        V_SF_ERR  =SF2016['V_SF_ERR']
        sf_dict = SF2016


    tfile = rt.TFile.Open(options.ifile,'read')
    
    histoDict = {}
    datahistDict = {}
    
    fLoose = None
    removeUnmatched=False
    iPt=-1
    for proc in (bkgs+sigs+['data_obs']):
        for box in boxes:
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box)).Clone()
            histoDict['%s_%s'%(proc,box)].Scale(GetSF(proc,box,tfile,fLoose,removeUnmatched,iPt,sf_dict))
            for syst in systs:
                if proc!='data_obs':
                    if syst!='mcstat':
                        #print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                        histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst)).Clone()
                        histoDict['%s_%s_%sUp'%(proc,box,syst)].Scale(GetSF(proc,box,tfile,fLoose,removeUnmatched,iPt,sf_dict))
                        #print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                        histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst)).Clone()
                        histoDict['%s_%s_%sDown'%(proc,box,syst)].Scale(GetSF(proc,box,tfile,fLoose,removeUnmatched,iPt,sf_dict))
                    else:
                        histoDict['%s_%s_%s%smuonCR%smcstatUp'%(proc,box,proc,box,options.year)] = tfile.Get('%s_%s'%(proc,box)).Clone(tfile.Get('%s_%s'%(proc,box)).GetName()+'_%s%smuonCR%smcstatUp'%(proc,box,options.year))
                        histoDict['%s_%s_%s%smuonCR%smcstatUp'%(proc,box,proc,box,options.year)].Scale(GetSF(proc,box,tfile,fLoose,removeUnmatched,iPt,sf_dict))
                        histoDict['%s_%s_%s%smuonCR%smcstatDown'%(proc,box,proc,box,options.year)] = tfile.Get('%s_%s'%(proc,box)).Clone(tfile.Get('%s_%s'%(proc,box)).GetName()+'_%s%smuonCR%smcstatDown'%(proc,box,options.year))
                        histoDict['%s_%s_%s%smuonCR%smcstatDown'%(proc,box,proc,box,options.year)].Scale(GetSF(proc,box,tfile,fLoose,removeUnmatched,iPt,sf_dict))
                        for ibin in range(1,histoDict['%s_%s'%(proc,box)].GetNbinsX()+1):
                            if histoDict['%s_%s'%(proc,box)].GetBinContent(ibin) <0:            ### Set negative bin to zero
                                histoDict['%s_%s'%(proc,box)].SetBinContent(ibin,0) 
                            histoDict['%s_%s_%s%smuonCR%smcstatUp'%(proc,box,proc,box,options.year)].SetBinContent(ibin, histoDict['%s_%s'%(proc,box)].GetBinContent(ibin)+ histoDict['%s_%s'%(proc,box)].GetBinError(ibin)) 
                            histoDict['%s_%s_%s%smuonCR%smcstatDown'%(proc,box,proc,box,options.year)].SetBinContent(ibin,max(1E-06, histoDict['%s_%s'%(proc,box)].GetBinContent(ibin)- histoDict['%s_%s'%(proc,box)].GetBinError(ibin))) 
    uncorrelate(histoDict, 'mcstat')

    
    outFile = 'datacard_muonCR.root'
    outFileHist = 'datacard_muonCR_hist.root'
    
    outputFile = rt.TFile.Open(options.odir+'/'+outFile,'recreate')
    w = rt.RooWorkspace('w_muonCR')
    #w.factory('y[40,40,201]')
    #w.var('y').setBins(1)
    w.factory('x[%i,%i,%i]'%(MASS_LO,MASS_LO,MASS_HI))
    w.var('x').setBins(MASS_BINS)

    outputFileHist = rt.TFile.Open(options.odir+'/'+outFileHist,'recreate')
    for key, histo in histoDict.iteritems():
        outputFileHist.cd()
        histo.Write(key)
        #histo.Rebin(23)
        #ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('y')),histo)
        ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('x')),histo)
        getattr(w,'import')(ds, rt.RooCmdArg())
    outputFileHist.Close()

    outputFile.cd()
    w.Write()
    outputFile.Close()
    txtfileName = outFile.replace('.root','.txt')

    writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,options)
    print '\ndatacard:\n'
    os.system('cat %s/%s'%(options.odir,txtfileName))



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--ifile', dest='ifile', default = './',help='directory with data', metavar='ifile')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option('--suffix', dest='suffix', default='', help='suffix for conflict variables',metavar='suffix')
    parser.add_option('--no-mcstat-shape', action='store_true', dest='noMcStatShape', default =False,help='change mcstat uncertainties to lnN', metavar='noMcStatShape')
    
    (options, args) = parser.parse_args()

    if options.suffix!='':
        options.suffix='_'+options.suffix
    main(options, args)
