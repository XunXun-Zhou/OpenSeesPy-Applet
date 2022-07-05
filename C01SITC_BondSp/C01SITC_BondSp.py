import openseespy.opensees as ops
import numpy as np
import os

expdata = np.loadtxt('exp.txt', skiprows = 2)
dexp = expdata[:, 0]

# Units: N mm MPa

# convert to British System: kip inch ksi
inch = 0.03937
ksi = 145.0377 / 1000
kip = 0.2248 / 1000

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Material Properties
# ======================================================
fc = 26.38 * ksi  # Concerte Compressive Strength
fyl = 497 * ksi   # Yielding Strength of Longitudinal Bars
ful = 592 * ksi   # Ultimate Strength of Longitudinal Bars
fyt = 459.5 * ksi # Yielding Strength of Transverse Ties
Elong = 200e3 * ksi # Young's Modulus of Longitudinal Bars
# ======================================================

# Specimen Geometry (Square Section)
# ======================================================
Height = 1400 * inch # Height of the Column
Width = 400 * inch   # Width of the Column
Cover = 34 * inch    # Thickness of Concrete Cover
# ======================================================

# Reinforcement Configuration
# ======================================================
dlongi = 19.05 * inch # Diameter of the Longitudinal Bars
dtrans = 6.35 * inch  # Diamter of the Transverse Bars
strans = 54 * inch    # Spacing of the Transverse Bars
# ======================================================

# Axial Force (Approximately 0.1 * fc * Ag)
# ======================================================
axial = -450e3 * kip # Magnitude of the axial force
# ======================================================

# Material Definition
# ======================================================
## Unconfined Concrete for Column (tag{1})
# ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
ops.uniaxialMaterial('Concrete01', 1, -fc, -0.002, 0, -0.006)

## Confined Concrete for Column (tag{2})
## ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
# ops.uniaxialMaterial('Concrete01', 2, -1.15 * fc, -0.005, -0.8 * 1.15 * fc, -0.015)
## ops.uniaxialMaterial('Concrete02', matTag, fpc, epsc0, fpcu, epsU, lambda, ft, Ets)
# ops.uniaxialMaterial('Concrete02', 2, -1.15 * fc, -0.005, -0.8 * 1.15 * fc, -0.015, 0.3, 0.1 * fc, 0.3 * 2 * 1.15 * fc / 0.005)
## ops.uniaxialMaterial('Concrete04', matTag, fc, epsc, epscu, Ec, fct, et, beta)
# ops.uniaxialMaterial('Concrete04', 2, -1.15 * fc, -0.005, -0.1, 5000 * (fc)**0.5, 0.1 * fc, 0.01, 0.15)
## ops.uniaxialMaterial('Concrete07', matTag, fc, epsc, Ec, ft, et, xp, xn, r)
# ops.uniaxialMaterial('Concrete07', 2, -1.15 * fc, -0.005, 5000 * (fc)**0.5, 0.1 * fc, 0.00024, 2, 30, 1.5)
## ops.uniaxialMaterial('Concrete01WithSITC', matTag, fpc, epsc0, fpcu, epsU, endStrainSITC=0.01)
ops.uniaxialMaterial('Concrete01WithSITC', 2, -1.15 * fc, -0.005, -0.8 * 1.15 * fc, -0.01)

## Longitudinal Bars for Column (tag{3})
## ops.uniaxialMaterial('Steel02', matTag, Fy, E0, b, *params, a1=a2*Fy/E0, a2=1.0, a3=a4*Fy/E0, a4=1.0, sigInit=0.0)
ops.uniaxialMaterial('Steel02', 3, fyl, Elong, 0.015, 20, 0.925, 0.15)
## uniaxialMaterial('ReinforcingSteel', matTag, fy, fu, Es, Esh, eps_sh, eps_ult, '-GABuck', lsr, beta, r, gamma, '-DMBuck', lsr, alpha=1.0, '-CMFatigue', Cf, alpha, Cd, '-IsoHard', a1=4.3, limit=1.0, '-MPCurveParams', R1=0.333, R2=18.0, R3=4.0)
# ops.uniaxialMaterial('ReinforcingSteel', 3, fyl, ful, Elong, 0.01 * Elong, 0.02, 0.2)

factor = 1.5
## Bond Slip for ZeroLengthSection Element (tag{4})
Sy = (0.1 * (dlongi / 4000 * (fyl * 1000) / ((fc * 1000)**0.5) * (2 * 0.4 + 1))**(1 / 0.4) + 0.013) * factor
# ops.uniaxialMaterial('Bond_SP01', matTag, Fy, Sy, Fu, Su, b, R)
ops.uniaxialMaterial('Bond_SP01', 4, fyl * factor, Sy, ful * factor, 35 * Sy, 0.5, 0.5)

## Elastic Shear Stiffness for ZeroLengthSection Element (tag{5})
# ops.uniaxialMaterial('Elastic', matTag, E, eta=0.0, Eneg=E)
ops.uniaxialMaterial('Elastic', 5, 1e10)

## Confined Concrete for ZeroLengthSection Element (tag{6})
# ops.uniaxialMaterial('Elastic', matTag, E, eta=0.0, Eneg=E)
ops.uniaxialMaterial('Concrete01', 6, -1.15 * fc, -0.005, -0.8 * 1.15 * fc, -0.015)

# ======================================================

# Section Definition
# ======================================================
## Column Section
# ops.section('Fiber', secTag, '-GJ', GJ)
ops.section('Fiber', 1)
# ops.patch('rect', matTag, numSubdivY, numSubdivZ, *crdsI, *crdsJ)
ops.patch('rect', 2, 10, 10, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover, -Width / 2 + Cover)
ops.patch('rect', 1, 10, 1, Width / 2, Width / 2, -Width / 2, Width / 2 - Cover)
ops.patch('rect', 1, 10, 1, Width / 2, -Width / 2 + Cover, -Width / 2, -Width / 2)
ops.patch('rect', 1, 1, 8, -Width / 2 + Cover, Width / 2 - Cover, -Width / 2, -Width / 2 + Cover)
ops.patch('rect', 1, 1, 8, Width / 2, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover)
# ops.layer('straight', matTag, numFiber, areaFiber, *start, *end)
ops.layer('straight', 3, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2)
ops.layer('straight', 3, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + dlongi / 2)
ops.layer('straight', 3, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2)
ops.layer('straight', 3, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2)

## Bond Slip
# ops.section('Fiber', secTag, '-GJ', GJ)
ops.section('Fiber', 2)
# ops.patch('rect', matTag, numSubdivY, numSubdivZ, *crdsI, *crdsJ)
ops.patch('rect', 6, 10, 10, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover, -Width / 2 + Cover)
ops.patch('rect', 1, 10, 1, Width / 2, Width / 2, -Width / 2, Width / 2 - Cover)
ops.patch('rect', 1, 10, 1, Width / 2, -Width / 2 + Cover, -Width / 2, -Width / 2)
ops.patch('rect', 1, 1, 8, -Width / 2 + Cover, Width / 2 - Cover, -Width / 2, -Width / 2 + Cover)
ops.patch('rect', 1, 1, 8, Width / 2, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover)
# ops.layer('straight', matTag, numFiber, areaFiber, *start, *end)
ops.layer('straight', 4, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2)
ops.layer('straight', 4, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + dlongi / 2)
ops.layer('straight', 4, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2)
ops.layer('straight', 4, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2)


## ops.section('Aggregator', secTag, *mats, '-section', sectionTag)
ops.section('Aggregator', 3, 5, 'Vy', '-section', 2)
# ======================================================

# Node Definition
# ======================================================
# ops.node(nodeTag, *crds, '-ndf', ndf, '-mass', *mass, '-disp', *disp, '-vel', *vel, '-accel', *accel)
ops.node(1, 0, 0 * Height / 5)
ops.node(2, 0, 0 * Height / 5) # Coincide with Node 1
ops.node(3, 0, 1 * Height / 5)
ops.node(4, 0, 2 * Height / 5)
ops.node(5, 0, 3 * Height / 5)
ops.node(6, 0, 4 * Height / 5)
ops.node(7, 0, 5 * Height / 5)
# ======================================================

# Element definition
# ======================================================
# ops.geomTransf('PDelta', transfTag, '-jntOffset', *dI, *dJ)
ops.geomTransf('PDelta', 1)
# ops.beamIntegration('Legendre', tag, secTag, N)
ops.beamIntegration('Legendre', 1, 1, 5)

## ops.element('zeroLengthSection', eleTag, *eleNodes, secTag, <'-orient', *vecx, *vecyp>, <'-doRayleigh', rFlag>)
ops.element('zeroLengthSection', 1, 1, 2, 3)

## element('forceBeamColumn', eleTag, *eleNodes, transfTag, integrationTag, '-iter', maxIter=10, tol=1e-12, '-mass', mass=0.0)
# ops.element('forceBeamColumn', 2, 2, 3, 1, 1)
# ops.element('forceBeamColumn', 3, 3, 4, 1, 1)
# ops.element('forceBeamColumn', 4, 4, 5, 1, 1)
# ops.element('forceBeamColumn', 5, 5, 6, 1, 1)
# ops.element('forceBeamColumn', 6, 6, 7, 1, 1)

## element('dispBeamColumn', eleTag, *eleNodes, transfTag, integrationTag, '-cMass', '-mass', mass=0.0)
ops.element('dispBeamColumn', 2, 2, 3, 1, 1)
ops.element('dispBeamColumn', 3, 3, 4, 1, 1)
ops.element('dispBeamColumn', 4, 4, 5, 1, 1)
ops.element('dispBeamColumn', 5, 5, 6, 1, 1)
ops.element('dispBeamColumn', 6, 6, 7, 1, 1)
# ======================================================

# Constraint definition
# ======================================================
# ops.fix(nodeTag, *constrValues)
ops.fix(1, 1, 1, 1)
# ======================================================

# Gravity Loadcase
# ======================================================
# ops.timeSeries('Linear', tag, '-factor', factor=1.0, '-tStart', tStart=0.0)
ops.timeSeries('Linear', 1)
# ops.pattern('Plain', patternTag, tsTag, '-fact', fact)
ops.pattern('Plain', 1, 1)
# ops.load(nodeTag, *loadValues)
ops.load(7, 0, axial, 0)

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGen')
ops.test('NormUnbalance', 1e-3, 100)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1)
ops.analysis('Static')
ok = ops.analyze(10)

print(ops.nodeDisp(7,2) / inch)

ops.loadConst('-time', 0)
# ======================================================

# Monotonic Lateral Loadcase
# ======================================================
os.remove('out_01SITC_full.txt')
ops.recorder('Node', '-file', 'out_01SITC_full.txt', '-time', '-node', 7, '-dof', 1, 'disp')
# ops.timeSeries('Linear', tag, '-factor', factor=1.0, '-tStart', tStart=0.0)
ops.timeSeries('Linear', 2)
# ops.pattern('Plain', patternTag, tsTag, '-fact', fact)
ops.pattern('Plain', 2, 2)
# ops.load(nodeTag, *loadValues)
ops.load(7, 1, 0, 0) # the reference force 1 along the axis x

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGen')

import SmartAnalyze
protocol = dexp * inch
# protocol = [100 * inch]
## SmartAnalyze.SmartAnalyzeStatic(node, dof, maxStep, targets)
SmartAnalyze.SmartAnalyzeStatic(7, 1, 0.1, protocol)
# ======================================================