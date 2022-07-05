import openseespy.opensees as ops
import numpy as np
import os

expdata = np.loadtxt('exp.txt', skiprows = 2)
dexp = expdata[:, 0]

# Units: N mm t MPa

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Material Properties
# ======================================================
fc = 26.38  # Concerte Compressive Strength
fyl = 497   # Yielding Strength of Longitudinal Bars
fyt = 459.5 # Yielding Strength of Transverse Ties
# ======================================================

# Specimen Geometry (Square Section)
# ======================================================
Height = 1400 # Height of the Column
Width = 400   # Width of the Column
Cover = 34    # Thickness of Concrete Cover
# ======================================================

# Reinforcement Configuration
# ======================================================
dlongi = 19.05 # Diameter of the Longitudinal Bars
dtrans = 6.35  # Diamter of the Transverse Bars
strans = 54    # Spacing of the Transverse Bars
# ======================================================

# Axial Force (Approximately 0.1 * fc * Ag)
# ======================================================
axial = -450e3 # Magnitude of the axial force
# ======================================================

# Material Definition
# ======================================================
## Unconfined Concrete
## ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
# ops.uniaxialMaterial('Concrete01', 1, fc, 0.002, 0.2 * fc, 0.006)
ops.uniaxialMaterial('ConcreteCM', 1, -32.0, -1673.6e-6, 3.44e4, 4.2538, 2.3, 2.80, 113.6e-6, 4.2538, 2, '-GapClose', 1)

## Confined Concrete
## ops.uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epsU)
# ops.uniaxialMaterial('Concrete01', 2, 1.15 * fc, 0.005, 0.8 * 1.2 * fc, 0.015)
## ops.uniaxialMaterial('Concrete02', matTag, fpc, epsc0, fpcu, epsU, lambda, ft, Ets)
# ops.uniaxialMaterial('Concrete02', 2, -1.15 * fc, -0.005, -0.8 * 1.2 * fc, -0.015, 0.3, 0.1 * fc, 0.3 * 2 * 1.15 * fc / 0.005)
## ops.uniaxialMaterial('Concrete04', matTag, fc, epsc, epscu, Ec, fct, et, beta)
# ops.uniaxialMaterial('Concrete04', 2, -1.15 * fc, -0.005, -0.1, 5000 * (fc)**0.5, 0.1 * fc, 0.01, 0.15)
## ops.uniaxialMaterial('Concrete07', matTag, fc, epsc, Ec, ft, et, xp, xn, r)
# ops.uniaxialMaterial('Concrete07', 2, -1.15 * fc, -0.005, 5000 * (fc)**0.5, 0.1 * fc, 0.00024, 2, 30, 1.5)
## ops.uniaxialMaterial('ConcreteCM', matTag, fpcc, epcc, Ec, rc, xcrn, ft, et, rt, xcrp, mon, '-GapClose', GapClose=0)
ops.uniaxialMaterial('ConcreteCM', 2, -1.15 * fc, -2230.3e-6, 3.44e4, 1.9165, 30, 2.80, 113.6e-6, 4.2538, 10000, '-GapClose', 1)

## Longitudinal Bars
## ops.uniaxialMaterial('Steel02', matTag, Fy, E0, b, *params, a1=a2*Fy/E0, a2=1.0, a3=a4*Fy/E0, a4=1.0, sigInit=0.0)
ops.uniaxialMaterial('Steel02', 3, fyl, 200e3, 0.01, 20, 0.925, 0.15)
# ======================================================

# Section Definition
# ======================================================
ops.section('Fiber', 1)
ops.patch('rect', 2, 10, 10, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover, -Width / 2 + Cover)
ops.patch('rect', 1, 10, 1, Width / 2, Width / 2, -Width / 2, Width / 2 - Cover)
ops.patch('rect', 1, 10, 1, Width / 2, -Width / 2 + Cover, -Width / 2, -Width / 2)
ops.patch('rect', 1, 1, 8, -Width / 2 + Cover, Width / 2 - Cover, -Width / 2, -Width / 2 + Cover)
ops.patch('rect', 1, 1, 8, Width / 2, Width / 2 - Cover, Width / 2 - Cover, -Width / 2 + Cover)
ops.layer('straight', 3, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - dlongi / 2)
ops.layer('straight', 3, 4, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + dlongi / 2)
ops.layer('straight', 3, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2, Width / 2 - Cover - dlongi / 2, Width / 2 - Cover - 1 / 3 * (Width - 2 * Cover - dlongi) - dlongi / 2)
ops.layer('straight', 3, 2, 0.25 * np.pi * dlongi**2, -Width / 2 + Cover + dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2, Width / 2 - Cover - dlongi / 2, -Width / 2 + Cover + 1 / 3 * (Width - 2 * Cover - dlongi) + dlongi / 2)
# ======================================================

# Node Definition
# ======================================================
ops.node(1, 0, 0 * Height / 5)
ops.node(2, 0, 5 * Height / 5)
# ======================================================

# Element definition
# ======================================================
ops.geomTransf('Linear', 1)
ops.beamIntegration('Legendre', 1, 1, 5)
ops.element('forceBeamColumn', 1, 1, 2, 1, 1)
## element('dispBeamColumn', eleTag, *eleNodes, transfTag, integrationTag, '-cMass', '-mass', mass=0.0)
# ops.element('dispBeamColumn', 1, 1, 2, 1, 1)
# ======================================================

# Constraint definition
# ======================================================
ops.fix(1, 1, 1, 1)
# ======================================================

# Gravity Loadcase
# ======================================================
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 0, axial, 0)

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGen')
ops.test('NormUnbalance', 1e-8, 100)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1)
ops.analysis('Static')
ops.analyze(10)

ops.loadConst('-time', 0)
# ======================================================

# Monotonic Lateral Loadcase
# ======================================================
# os.remove('out_CM1.txt')
ops.recorder('Node', '-file', 'out_CM1.txt', '-time', '-node', 2, '-dof', 1, 'disp')
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 200, 2)
ops.load(2, 1, 0, 0)

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGen')

import SmartAnalyze
# protocol = dexp
protocol = [100, -100, 100, -100, 0]
SmartAnalyze.SmartAnalyzeStatic(2, 1, 0.1, protocol)
# ======================================================