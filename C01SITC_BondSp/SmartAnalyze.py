# -*- coding: utf-8 -*-
"""
File: SmartAnalyze.py
Created on Sun Jun 28 20:24:24 2020
Author: Difang Huang 榛勭媱鏄�

README:
   Introduction
   ----------------------------------------------------------------------------
   The SmartAnalyze provides OpenSees users a easier way to conduct analyses.
   There are two main functions defined in this .py file. SmartAnalyzeTransient & SmartAnalyzeStatic.
   
   SmartAnalyzeTransient is used to conduct time history analyses.
        The arguments must be specified are:
            dt: delta t
            npts: number of points.
   
    SmartAnalyzeStatic is used to conduct static analyze.
        Users provide a loading protocol with displacement targets.
        Then SmartAnalyze will run DisplacementControl analyses accordingly.
        The arguments that must be specified are:
            node: the node tag in the displacement control
            dof: the dof in the displacement control
            maxStep: the maximum step length in the displacement control
            targets: a list of target displacements.
                (E.g. {1 -1 1 -1 0} will result in cyclic load of disp amplitude 1 twice.)
                Note: the first element must be positive.
    
    If the control array is not specified, all the default values will be used.
    If you want to change the control parameters, pass it as an array delegate.
    
    Example
    ---------------------------------------------------------------------------
    Example 1: Basic usage for Transient
        import SmartAnalyze
        constraints('Transformation')
        numberer('Plain')
        system('BandGeneral')
        integrator('Newmark', 0.5, 0.25)
        SmartAnalyzeTransient(dt, npts)
    
    Example 2: Basic usage for Static 
        import SmartAnalyze
        constraints('Transformation')
        numberer('Plain')
        system('BandGeneral')
        protocol=[1, -1, 1, -1, 0]
        SmartAnalyzeStatic(node, dof, maxStep, protocol)
    
    Example 3: change control parameters
        control['printPer']=20
        control['tryAlterAlgoTypes']=True
        control['algoTypes']=[20, 30]
        SmartAnalyzeTransient(dt, npts, control)
        
    Example 4: define user algorithm
        def UserAlgorithm0():
            algorithm('KrylovNewton', increment='initial', maxDim=10)
        control['algoTypes']=[80]
        SmartAnalyzeTransient(dt, npts, control)
    
    The work flow
    ---------------------------------------------------------------------------
        1. Start
        2. Set initial step length, algorithm method and test (You don't need to specify them in your model.)
        3. Divide the whole analysis into pieces. For Static, use maxStep. For Transient, use dt.
        4. Loop by each piece and analyze recursively with RecursiveAnalyze, in the following way
            4.1 Trail analyze for one step, if converge, continue loop 4.
            4.2 If not converge, if tryAddTestTimes is True, if the last test norm is smaller than normTol, recursively set a larger test time.
            4.3 If not converge, if tryAlterAlgoTypes is True, recursively loop to the next algo type.
            4.4 If not converge, divide the current step into two steps. The first one equals to the current step times relaxation.
            4.5 If either step is smaller than minStep:
                4.5.1 If tryLooseTestTol is True, loose test tolerance to looseTestTolTo.
                4.5.2 Else, return not converge code. Exit.
            4.6 If both steps are not smaller than minStep, divide the current piece into two and re-run loop 4.
        5. If converge, return success message.
    
    Control Parameters
    ---------------------------------------------------------------------------
    TEST RELATED:
        `testType`        : string. Identical to the testType in OpenSees test command. Default is "EnergyIncr".
                            Choices see http://opensees.berkeley.edu/wiki/index.php/Test_Command.
        `testTol`         : float. The initial test tolerance set to the OpenSees test command. Default is 1.0e-6.
                            If tryLooseTestTol is set to True, the test tolerance can be loosen.
        `testIterTimes`   : integer. The initial number of test iteration times. Default is 7.
                            If tryAddTestTimes is set to True, the number of test times can be enlarged.
        `testPrintFlag`   : integer. The test print flag in OpenSees Test command. Default is 0.
                            Choices see http://opensees.berkeley.edu/wiki/index.php/Test_Command.
        `tryAddTestTimes` : boolean. Default is True If this is set to True, 
                            the number of test times will be enlarged if the last test norm is smaller than `normTol`,
                            the enlarged number is specified in `testIterTimesMore`.
                            Otherwise, the number of test times will always be equal to `testIterTimes`.
        `normTol`         : float. Only useful when tryAddTestTimes is True. Default is 1.0e3.
                            If unconverge, the last norm of test will be compared to `normTol`.
                            If the norm is smaller, the number of test times will be enlarged.
        `testIterTimesMore` : integer. Only useful when tryaddTestTimes is True. Default is 50.
                            If unconverge and norm is ok, the test iteration times will be set to this number.
        `tryLooseTestTol` : boolean. If this is set to True, if unconverge at minimum step,
                            the test tolerance will be loosen to the number specified by `looseTestTolTo`.
                            the step will be set back.
                            Default is True.
        `looseTestTolTo`  : float. Only useful if tryLooseTestTol is True.
                            If unconvergance at the min step, the test tolerance will be set to this value.
                            Default is 1.0
    
    ALGORITHM RELATED:
        `tryAlterAlgoTypes` : boolean. Default is False.
                              If True, different algorithm types specified in `algoTypes` will be tried during unconvergance.
                              If False, the first algorithm type specified in `algoTypes` will be used.
        `algoTypes`         : list of integer. A list of flags of the algorithms to be used during unconvergance.
                              The integer flag is documented in the following section.
                              Only useful when tryAlterAlgoTypes is True.
                              The first flag will be used by default.
                              The algorithm command in the model will be ignored.
                              Default is { 40 }
                              If you need other algorithm, try a user-defined algorithm. See the following section.
        
    STEP RELATED:
        `initialStep`     : float. Default is equal to $dt.
                            Specifying the initial Step length to conduct analysis.
        `relaxation`      : float, between 0 and 1. Default is 0.5.
                            A factor that is multiplied by each time the step length is shortened.
        `minStep`         : float. Default is 1.0e-6.
                            The step tolerance when shortening the step length.
                            If step length is smaller than minStep, special ways to converge the model will be used according to `try-` flags.
    
    LOGGING RELATED:
        `printPer`        : integer. Print to the console every several trials. Default is 10.
        `debugMode`       : boolean. Print as much information as possible.
    
    Algorithm type flag reference
    ---------------------------------------------------------------------------
     0:  Linear
     1:  Linear -initial
     2:  Linear -factorOnce
    10:  Newton
    11:  Newton -initial
    12:  Newton -initialThenCurrent
    20:  NewtonLineSearch
    21:  NewtonLineSearch -type Bisection
    22:  NewtonLineSearch -type Secant
    23:  NewtonLineSearch -type RegulaFalsi
    30:  ModifiedNewton
    31:  ModifiedNewton -initial
    40:  KrylovNewton
    41:  KrylovNewton -iterate initial
    42:  KrylovNewton -increment initial
    43:  KrylovNewton -iterate initial -increment initial
    44:  KrylovNewton -maxDim 6
    50:  SecantNewton
    51:  SecantNewton -iterate initial
    52:  SecantNewton -increment initial 
    53:  SecantNewton -iterate initial -increment initial
    60:  BFGS
    70:  Broyden    
    80:  PeriodicNewton
    90:  User-defined0
    
    About User-defined algoType:
        If special algorithm is to be used, SmartAyalize provides 3 user-defined algorithms.
        The script author should specify the algorithm as a procedure in the script.
        The script name must be `UserAlgorithm0`, `UserAlgorithm1`, `UserAlgorithm2`.
        Example see section Example No. 4.
        
    Change Log
    ---------------------------------------------------------------------------
    Mon Jun 29 16:10:18 2020 v0.0
        Creat SmartAnalyze.py file.
        
"""

from openseespy.opensees import * 
import time


def SmartAnalyzeTransient(dt, npts, ud=''):
    '''
    dt: delta t
    npts: number of points
    ud: change the control parameters in control dict
    '''
    # default control parameters
    control={}
    control['analysis']="Transient"
    control['testType']="EnergyIncr"
    control['testTol']=1.0e-6
    control['testIterTimes']=7
    control['testPrintFlag']=0
    control['tryAddTestTimes']=False
    control['normTol']=1.0e3
    control['testIterTimesMore']=50
    control['tryLooseTestTol']=False
    control['looseTestTolTo']=1.0
    control['tryAlterAlgoTypes']=False
    control['algoTypes']=[40]                              
    control['initialStep']=dt
    control['relaxation']=0.5
    control['minStep']=1.0e-6
    control['printPer']=10
    control['debugMode']=False
    
    # set user control parameters
    if ud!='':
        userControl=ud                                      
        control.update(userControl)
    
    print("Control parameters:")
    for key,value in control.items():
        print(key, value)
    
    # initialize analyze commands
    test(control['testType'],control['testTol'],control['testIterTimes'],control['testPrintFlag'])
    setAlgorithm(control['algoTypes'][0])
    analysis('Transient')
    
    # set an array to store current status.
    current={}
    current['startTime']=time.time()
    current['algoIndex']=0
    current['testIterTimes']=control['testIterTimes']
    current['testTol']=control['testTol']
    current['counter']=0
    current['progress']=0
    current['segs']=npts
    
    # divide the whole process into segments.
    #鎶婃椂绋嬫寜鐓ф暟鎹偣鍒嗕负鍚勪釜灏忔seg杩涜鍒嗘瀽
    for seg in range(1,npts+1):
        ok=RecursiveAnalyze(control['initialStep'],0,control['testIterTimes'],control['testTol'],control,current)
        #濡傛灉閫掑綊鍚庝笉鏀舵暃锛岃烦鍑哄嚱鏁帮紝鏄剧ず鍒嗘瀽澶辫触鍜岀敤鏃�
        if ok<0:
            print(">>> SmartAnalyze: Analyze failed. Time consumption: %f s." %(time.time()-current['startTime']))
            return ok
        
        #璇ユ暟鎹偣鍒嗘瀽鏀舵暃锛屾洿鏂版垚鍔熷垎鏋愮殑鐐规暟
        current['progress']=seg
        
        #鏄剧ず瀹炴椂鎴愬姛鍒嗘瀽鐨勮繃绋嬪崰鎬昏繃绋嬬殑鐧惧垎姣�
        if control['debugMode']:
            print("*** SmartAnalyze: progress %f" %(current['progress']/current['segs']))
    
    #鍏ㄩ儴鏁版嵁鐐瑰垎鏋愭垚鍔燂紝鏄剧ず鍒嗘瀽鎴愬姛鍜岀敤鏃�
    print(">>> SmartAnalyze: Successfully finished! Time consumption: %f s." %(time.time()-current['startTime']))


def SmartAnalyzeStatic(node, dof, maxStep, targets, ud=''):
    '''
    node: the node tag in the displacement control
    dof: the dof in the displacement control
    maxStep: the maximum step length in the displacement control
    targets: a list of target displacements, the first element must be positive
    ud: change the control parameters in control dict
    '''
    # set initial step
    if maxStep>targets[0]:
        initialStep=targets[0]
    else:
        initialStep=maxStep
    
    # default control parameters
    control={}
    control['analysis']="Static"
    control['testType']="EnergyIncr"
    control['testTol']=1.0e-6
    control['testIterTimes']=7
    control['testPrintFlag']=0
    control['tryAddTestTimes']=False
    control['normTol']=1.0e3
    control['testIterTimesMore']=50
    control['tryLooseTestTol']=False
    control['looseTestTolTo']=1.0
    control['tryAlterAlgoTypes']=False
    control['algoTypes']=[40]
    control['initialStep']=initialStep
    control['relaxation']=0.5
    control['minStep']=1.0e-6
    control['printPer']=10
    control['debugMode']=False
    
    # set user control parameters
    if ud!='':
        userControl=ud
        control.update(userControl)
    
    print("Control parameters:")
    for key,value in control.items():
        print(key, value)
    
    # initialize analyze commands
    test(control['testType'],control['testTol'],control['testIterTimes'],control['testPrintFlag'])
    setAlgorithm(control['algoTypes'][0])
    integrator('DisplacementControl', node, dof, initialStep)
    analysis('Static')
    
    # set an array to store current status.
    current={}
    current['startTime']=time.time()
    current['algoIndex']=0
    current['testIterTimes']=control['testIterTimes']
    current['testTol']=control['testTol']
    current['counter']=0
    current['progress']=0
    current['step']=initialStep
    current['node']=node
    current['dof']=dof
    
    # calcuate whole distance; divide the whole process into segments.
    distance=0
    segs=[]                                          #鎶婃暣涓姞杞借繃绋嬪垎瑙ｄ负闀垮害涓嶈秴杩噈axStep鐨勶紝甯︽璐熸柟鍚戠殑灏忓姞杞芥
    for i in range(len(targets)):                    #鐩爣浣嶇Щ鍒楄〃寰幆
        if i==0:                                     #绗竴娈典綅绉�
            section=targets[0]                       #鎺ㄨ浣嶇Щ鐩存帴灏辨槸鍒楄〃绗竴涓綅绉�
            positive=True                            #姝ｅ悜 
        else:                                        #闈炵涓€娈典綅绉�
            section=targets[i]-targets[i-1]          #鎺ㄨ浣嶇Щ涓虹洰鏍囦綅绉诲噺鍘讳笂涓€娈电洰鏍囦綅绉�
            if section>=0:                           #鑻ュぇ浜庨浂涓烘鍚戞帹
                positive=True           
            else:                                    #鑻ュ皬浜庨浂涓鸿礋鍚戞帹
                positive=False
        
        distance=distance+abs(section)               #鎵€鎺ㄧ殑缁濆浣嶇Щ鎬诲拰锛宻ection涓烘瘡娆″崟鎺ㄧ殑璺濈
        
        if positive:                                 #鑻ョ洰鍓嶅浜庢鍚戝姞杞�
            j=0
            while (section-j*maxStep)>maxStep:       #鎶婃湰娈垫帹瑕嗕綅绉诲垎涓洪暱搴︿负maxStep鐨勫悇涓皬娈碉紝瀛樹簬鍒楄〃segs涓�
                segs.append(maxStep)
                j+=1
            segs.append(section-j*maxStep)           #鏈€鍚庝竴灏忔涓嶈冻maxStep鐨勪篃瀛樹簬segs
            
        else:                                        #鑻ョ洰鍓嶅浜庤礋鍚戝姞杞�
            j=0
            while (-section-j*maxStep)>maxStep:      #鎶婃湰娈垫帹瑕嗕綅绉诲垎涓洪暱搴︿负maxStep鐨勫悇涓皬娈碉紝瀛樹簬鍒楄〃segs涓�
                segs.append(-maxStep)
                j+=1
            segs.append(section+j*maxStep)           #鏈€鍚庝竴灏忔涓嶈冻maxStep鐨勪篃瀛樹簬segs
    
    current['segs']=len(segs)                        #鏁翠釜鍔犺浇杩囩▼涓墍鏈夊皬鍔犺浇娈电殑涓暟
    
    # Run recursive analysis
    #瀵规瘡涓皬鍔犺浇娈佃繘琛岃绠�
    for seg in segs:
        ok=RecursiveAnalyze(seg, 0, control['testIterTimes'], control['testTol'], control, current)
        if ok<0:               #鑻ヤ笉鏀舵暃锛岃烦鍑哄嚱鏁板苟鏄剧ず鐢ㄦ椂
            print(">>> SmartAnalyze: Analyze failed. Time consumption: %f s." %(time.time()-current['startTime']))
            return ok
        #鏀舵暃锛屾垚鍔熷垎鏋愮殑杩囩▼鏁�+1
        current['progress']+=1
        
        #鏄剧ず鎴愬姛鍒嗘瀽鐨勮繃绋嬫暟鍗犳€荤殑鍔犺浇娈垫暟鐨勭櫨鍒嗘瘮
        if control['debugMode']:
            print("*** SmartAnalyze: progress %f" %(current['progress']/current['segs']))
    
    #鍏ㄩ儴鍔犺浇娈靛垎鏋愬畬鎴愶紝鏄剧ず鎴愬姛瀹屾垚鍒嗘瀽鍜岀敤鏃�
    print(">>> SmartAnalyze: Successfully Finished! Time consumption: %f s." %(time.time()-current['startTime']))
    
    
    
    
    

def RecursiveAnalyze(step, algoIndex, testIterTimes, testTol, vcontrol, vcurrent):
    '''
    step: 姝ラ暱锛屽姩鍔涘垎鏋愪负dt; 闈欏姏鍒嗘瀽涓哄皬鍔犺浇娈电殑浣嶇Щ锛�<=maxStep
    algoIndex: 鍒濆杩唬鏂规硶鍒楄〃鐨勫簭鍙凤紝涓€鑸粠绗竴涓紑濮嬶紝鍗充负0
    testIterTimes: 杩唬娆℃暟锛岄粯璁や负7
    testTol: 杩唬瀹瑰樊锛岄粯璁や负1.0e-6
    vcontrol: 鎺у埗鍙傛暟瀛楀吀
    vcurrent: 鐘舵€佸弬鏁板瓧鍏�
    '''
    control=vcontrol
    current=vcurrent
    
    print('CONTROL PARAMETERS:')
    print(control)
    print('CURRENT STATE PARAMETERS:')
    print(current)
    print('\n')
    
    #杈撳嚭鏈鍒嗘瀽鐨勫弬鏁�
    if control['debugMode']:
        print("*** SmartAnalyze: Run Recursive: step=%f, algoI=%i, times=%i, tol=%f" %(step, algoIndex, testIterTimes, testTol))
        print('\n')
    
    #鏀瑰彉杩唬鏂规硶
    if algoIndex!=current['algoIndex']:
        print(">>> SmartAnalyze: Setting algorithm to %i" %(control['algoTypes'][algoIndex]))
        print('\n')
        setAlgorithm(control['algoTypes'][algoIndex])
        current['algoIndex']=algoIndex
    
    #鍙樺寲杩唬娆℃暟鍜屽宸�
    if testIterTimes!=current['testIterTimes'] or testTol!=current['testTol']:
        if testIterTimes!=current['testIterTimes']:
            print(">>> SmartAnalyze: Setting test iteration times to %i" %(testIterTimes))
            print('\n')
            current['testIterTimes']=testIterTimes
        if testTol!=current['testTol']:
            print("SmartAnalyze: Setting test tolerance to %f" %(testTol))
            print('\n')
            current['testTol']=testTol
            
        test(control['testType'], testTol, testIterTimes, control['testPrintFlag'])
    
    #闈欏姏鍒嗘瀽淇敼姝ラ暱
    if control['analysis']=='Static' and current['step']!=step:
        print(">>> SmartAnalyze: Setting step to %f" %(step))
        print('\n')
        integrator('DisplacementControl', current['node'], current['dof'], step)
        current['step']=step
    
    # trial analyze once
    #闈欏姏鍒嗘瀽
    if control['analysis']=='Static':
        ok=analyze(1)
    #鍔ㄥ姏鍒嗘瀽
    else:
        ok=analyze(1, step)
    
    #鍗曟鍒嗘瀽娆℃暟璁板綍
    current['counter']+=1
    
    #鍒嗘瀽鏀舵暃 璺冲嚭鍑芥暟 寮€濮嬩笅涓€灏忔鐨勮绠�
    if ok==0:
        #婊℃寚瀹氭鏁板氨杈撳嚭瀹屾垚鐧惧垎姣斿拰鐢ㄦ椂
        if current['counter']>=control['printPer']:
            print("* SmartAnalyze: progress %f. Time consumption: %f s." 
                  %(current['progress']/current['segs'], (time.time()-current['startTime'])/1000.0))
            print('\n')
            current['counter']=0
        return 0
    
    # 鍒嗘瀽涓嶆敹鏁� 寮€濮嬫敼鍙樺弬鏁伴€掑綊
    # Add test iteration times. Use current step, algorithm and test tolerance.
    if control['tryAddTestTimes'] and testIterTimes!=control['testIterTimesMore']:
        #妫€鏌ヨ寖鏁�
        norm=getCTestNorms()
        #濡傛灉鑼冩暟灏忎簬瑙勫畾鍊硷紝澧炲姞杩唬娆℃暟锛屽叾浠栧弬鏁颁笉鍙橈紝鏈嚱鏁伴€掑綊
        if norm[-1]<control['normTol']:
            print(">>> SmartAnalyze: Adding test times to %i." %(control['testIterTimesMore']))
            print('\n')
            return RecursiveAnalyze(step, algoIndex, control['testIterTimesMore'], testTol, control, current)
        #濡傛灉鑼冩暟澶т簬瑙勫畾鍊硷紝涓嶅鍔�
        else:
            print(">>> SmartAnalyze: Not adding test times for norm %f" %(norm[-1]))
            print('\n')
    
    # Change algorithm. Set back test iteration times.
    # 濡傛灉杩唬鏂规硶搴忓彿杩樻病瓒� 灏濊瘯涓嬩竴绉嶈凯浠ｆ柟娉�
    if control['tryAlterAlgoTypes'] and (algoIndex+1)<len(control['algoTypes']):
        algoIndex+=1
        print(">>> SmartAnalyze: Setting algorithm to  %i." %(control['algoTypes'][algoIndex]))
        print('\n')
        return RecursiveAnalyze(step, algoIndex, testIterTimes, testTol, control, current)
    
    # If step length is too small, try add test tolerance. set algorithm and test iteration times back.
    if abs(step)<2*control['minStep']:
        print(">>> SmartAnalyze: current step %f is too small!" %(step))
        print('\n')
        if control['tryLooseTestTol'] and current['testTol']!=control['looseTestTolTo']:
            print("!!! SmartAnalyze: Warning: Loosing test tolerance")
            print('\n')
            return RecursiveAnalyze(step, 0, control['testIterTimes'], control['looseTestTolTo'], control, current)
        
        # Here, all methods have been tried. Return negative value.
        return -1
    
    # Split the current step into two steps.
    stepNew=step*control['relaxation']
    if stepNew>0 and stepNew<control['minStep']:
        stepNew=control['minStep']
    
    if stepNew<0 and stepNew>-control['minStep']:
        stepNew=-control['minStep']
    
    stepRest=step-stepNew
    print(">>> SmartAnalyze: Dividing the current step %f into %f and %f" %(step, stepNew, stepRest))
    print('\n')
    ok=RecursiveAnalyze(stepNew, 0, testIterTimes, testTol, control, current)
    if ok<0:
        return -1
    ok=RecursiveAnalyze(stepRest, 0, testIterTimes, testTol, control, current)
    if ok<0:
        return -1
    return 1
        
        
    

def setAlgorithm(algotype):
    '''
    
    '''
    def case0():
        print("> SmartAnalyze: Setting algorithm to  Linear ...")
        algorithm('Linear')
    
    def case1():
        print("> SmartAnalyze: Setting algorithm to  Linear -initial ...")
        algorithm('Linear', initial=True)
    
    def case2():
        print("> SmartAnalyze: Setting algorithm to  Linear -factorOnce ...")
        algorithm('Linear', factorOnce=True)
        
    def case10():
        print("> SmartAnalyze: Setting algorithm to  Newton ...")
        algorithm('Newton')
    
    def case11():
        print("> SmartAnalyze: Setting algorithm to  Newton -initial ...")
        algorithm('Newton', initial=True)
    
    def case12():
        print("> SmartAnalyze: Setting algorithm to  Newton -initialThenCurrent ...")
        algorithm('Newton', initialThenCurrent=True)
    
    def case20():
        print("> SmartAnalyze: Setting algorithm to  NewtonLineSearch ...")
        algorithm('NewtonLineSearch')
    
    def case21():
        print("> SmartAnalyze: Setting algorithm to  NewtonLineSearch -type Bisection ...")
        algorithm('NewtonLineSearch', True)
    
    def case22():
        print("> SmartAnalyze: Setting algorithm to  NewtonLineSearch -type Secant ...")
        algorithm('NewtonLineSearch', Secant=True)
    
    def case23():
        print("> SmartAnalyze: Setting algorithm to  NewtonLineSearch -type RegulaFalsi ...")
        algorithm('NewtonLineSearch', RegulaFalsi=True)
    
    def case30():
        print("> SmartAnalyze: Setting algorithm to  Modified Newton ...")
        algorithm('ModifiedNewton')
    
    def case31():
        print("> SmartAnalyze: Setting algorithm to  ModifiedNewton -initial ...")
        algorithm('ModifiedNewton', False, True)
    
    def case40():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton ...")
        algorithm('KrylovNewton')
    
    def case41():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton -iterate initial ...")
        algorithm('KrylovNewton', iterate='initial')
    
    def case42():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton -increment initial ...")
        algorithm('KrylovNewton', increment='initial')
    
    def case43():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton -iterate initial -increment initial ...")
        algorithm('KrylovNewton', iterate='initial', increment='initial')
    
    def case44():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton -maxDim 50")
        algorithm('KrylovNewton', maxDim=50)
    
    def case45():
        print("> SmartAnalyze: Setting algorithm to  KrylovNewton -iterate initial -increment initial -maxDim 50")
        algorithm('KrylovNewton', iterate='initial', increment='initial', maxDim=50)
    
    def case50():
        print("> SmartAnalyze: Setting algorithm to  SecantNewton ...")
        algorithm('SecantNewton')

    def case51():
        print("> SmartAnalyze: Setting algorithm to  SecantNewton -iterate initial ...")
        algorithm('SecantNewton', iterate='initial')
    
    def case52():
        print("> SmartAnalyze: Setting algorithm to  SecantNewton -increment initial  ...")
        algorithm('SecantNewton', increment='initial')
    
    def case53():
        print("> SmartAnalyze: Setting algorithm to  SecantNewton -iterate initial -increment initial ...")
        algorithm('SecantNewton', iterate='initial', increment='initial')
    
    def case60():
        print("> SmartAnalyze: Setting algorithm to  BFGS ...")
        algorithm('BFGS')
    
    def case70():
        print("> SmartAnalyze: Setting algorithm to  Broyden ...")
        algorithm('Broyden')
    
    def case80():
        print("> SmartAnalyze: Setting algorithm to  PeriodicNewton ...")
        algorithm('PeriodicNewton')
    
    def case90():
        #UserAlgorithm0
        pass
        
    def default():
        print("!!! SmartAnalyze: ERROR! WRONG Algorithm Type!")
    
    
    switch={'0':case0, '1':case1, '2':case2, '10':case10,'11':case11, '12':case12,
            '20':case20, '21':case21, '21':case21, '23':case23,
            '30':case30, '31':case31, '40':case40, '41':case41, '42':case42, '43':case43, '44':case44, '45':case45,
            '50':case50, '51':case51,'52':case52,'53':case53, '60':case60, '70':case70, '80':case80, '90':case90, 'default':default}
    
    choice=str(algotype)
    switch.get(choice, default)()
    














































