import matplotlib.pyplot as plt
import numpy as np
import openseespy.opensees as op


def InelasticResponse(mass, k_init, f_y, motion, dt, xi=0.05, r_post=0.0):
    """
    Run seismic analysis of a nonlinear SDOF

    :param mass: SDOF mass
    :param k_init: spring stiffness
    :param f_y: yield strength
    :param motion: list, acceleration values
    :param dt: float, time step of acceleration values
    :param xi: damping ratio
    :param r_post: post-yield stiffness
    :return:
    """

    op.wipe()
    op.model('basic', '-ndm', 2, '-ndf', 3)  # 2 dimensions, 3 dof per node

    # Establish nodes
    bot_node = 1
    top_node = 2
    op.node(bot_node, 0., 0.)
    op.node(top_node, 0., 0.)

    # Fix bottom node
    op.fix(top_node, 0, 1, 1)
    op.fix(bot_node, 1, 1, 1)
    # Set out-of-plane DOFs to be slaved
    op.equalDOF(1, 2, *[2, 3])

    # nodal mass (weight / g):
    op.mass(top_node, mass, 0., 0.)

    # Define material
    bilinear_mat_tag = 1
    mat_type = "Steel01"
    mat_props = [f_y, k_init, r_post]
    op.uniaxialMaterial(mat_type, bilinear_mat_tag, *mat_props)

    # Assign zero length element
    beam_tag = 1
    op.element('zeroLength', beam_tag, bot_node, top_node, "-mat",
               bilinear_mat_tag, "-dir", 1, '-doRayleigh', 1)

    # Define the dynamic analysis
    load_tag_dynamic = 1
    pattern_tag_dynamic = 1

    values = list(-1 * motion)  # should be negative
    op.timeSeries('Path', load_tag_dynamic, '-dt', dt, '-values', *values)
    op.pattern('UniformExcitation', pattern_tag_dynamic,
               1, '-accel', load_tag_dynamic)

    # set damping based on first eigen mode
    angular_freq = op.eigen('-fullGenLapack', 1)[0] ** 0.5
    alpha_m = 0.0
    beta_k = 2 * xi / angular_freq
    beta_k_comm = 0.0
    beta_k_init = 0.0

    op.rayleigh(alpha_m, beta_k, beta_k_init, beta_k_comm)

    # Run the dynamic analysis

    op.wipeAnalysis()

    op.algorithm('Newton')
    op.system('SparseGeneral')
    op.numberer('RCM')
    op.constraints('Transformation')
    op.integrator('Newmark', 0.5, 0.25)
    op.analysis('Transient')

    tol = 1.0e-10
    iterations = 10
    op.test('EnergyIncr', tol, iterations, 0, 2)
    analysis_time = (len(values) - 1) * dt
    analysis_dt = 0.001
    outputs = {
        "time": [],
        "rel_disp": [],
        "rel_accel": [],
        "rel_vel": [],
        "force": []
    }

    while op.getTime() < analysis_time:
        curr_time = op.getTime()
        op.analyze(1, analysis_dt)
        outputs["time"].append(curr_time)
        outputs["rel_disp"].append(op.nodeDisp(top_node, 1))
        outputs["rel_vel"].append(op.nodeVel(top_node, 1))
        outputs["rel_accel"].append(op.nodeAccel(top_node, 1))
        op.reactions()
        # Negative since diff node
        outputs["force"].append(-op.nodeReaction(bot_node, 1))
    op.wipe()
    for item in outputs:
        outputs[item] = np.array(outputs[item])

    return outputs


# 读取地震波数据
record_filename = 'test_motion_dt0p01.txt'
motion_step = 0.01
rec = np.loadtxt(record_filename)

# 指定初始刚度（通过指定质量及弹性周期）及相关参数
period = 1.0
mass = 1.0
k_spring = 4 * np.pi ** 2 * mass / period ** 2
f_yield = 2
xi = 0.05
r_post = 0.0

'''
# 指定初始刚度（通过指定质量及弹性刚度）及相关参数
mass = 1.0
k_spring = 39.47841760435743
f_yield = 1.5
xi = 0.05
r_post = 0.0

# 指定初始刚度（通过指定弹性周期及弹性刚度）及相关参数
period = 1.0
k_spring = 39.47841760435743
mass = k_spring * period ** 2 / (4 * np.pi ** 2)
f_yield = 1.5
xi = 0.05
r_post = 0.0
'''

outputs = InelasticResponse(mass, k_spring, f_yield, rec, motion_step, xi, r_post)
ux_opensees = outputs["rel_disp"]
plt.plot(outputs["time"], ux_opensees, label="Fy=%.3gN" % f_yield)
plt.legend()
plt.show()
