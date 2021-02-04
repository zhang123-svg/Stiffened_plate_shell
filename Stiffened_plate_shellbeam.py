#!/user/bin/python
#-*-coding:UTF-8-*-

#文件名：Stiffened_plate_shellbeam.py

#运行该脚本将自动实现加筋平板的屈曲分析(等效模型)
import math

from abaqus import *
import testUtils
testUtils.setBackwardCompatibility()
from abaqusConstants import *

#建立模型
myModel = mdb.Model(name='Stiffened_plate_shellbeam')
#删除Model-1
del mdb.models['Model-1']


#导入part模块
import part
import regionToolset

tol = 0.1

#输入Plate几何参数        
t_fields = (('Length (mm)','500'),('Width (mm)','200'),('Thickness (mm)','4'))
p_Length, p_Width, p_Thickness = getInputs(fields=t_fields, label='Plate dimensions:', dialogTitle='Create Plate')
length = float(p_Length)
width = float(p_Width)
thickness = float(p_Thickness)
#创建草图
myPlateSketch = myModel.ConstrainedSketch(name='Stiffened_plate_shellbeam',sheetSize=1000.0)

#绘制平板
myPlateSketch.rectangle(point1=(0.0,0.0), point2=(length,width))

#创建平板模型
myPlatePart = myModel.Part(name='Stiffened_plate_shellbeam', 
    dimensionality=THREE_D, type=DEFORMABLE_BODY)

#创建二维shell平板
myPlatePart.BaseShell(sketch=myPlateSketch)

#创建平板的set：set-plate             
Platefaces = myPlatePart.faces.findAt(((0,0,0),))
myPlatePart.Set(name='Set-plate', faces=(Platefaces,))

#输入与载荷平行方向的加强筋St的参数  注意要float参数
t_fields = (('S_Height (mm)','10'),('S_UpWidth (mm)','8'),('S_BotWidth (mm)','8'),('S_Pitch (mm)','25'),('S_Number (mm)','8'),)
p_SHeight, p_SUpWidth, p_SBotWidth, p_SPitch, p_SNum = getInputs(fields=t_fields, label='Stringer Dimension:', dialogTitle='Create Stringer')
Sheight = float(p_SHeight)
Supwidth = float(p_SUpWidth)
Sbotwidth = float(p_SBotWidth)
Snum = int(p_SNum)
Spitch = float(p_SPitch)


#绘制加强筋Stringer
#计算palte边界到第一个Stringer中心的距离
eachcenterleft = (width-(Snum-1)*Spitch)/2

#绘制加强筋stringer的草图
Upedge = myPlatePart.edges.findAt((length,tol,0),)
Upface = myPlatePart.faces.findAt((tol,tol,0),)
tr = myPlatePart.MakeSketchTransform(sketchPlane=Upface, sketchUpEdge=Upedge, 
    sketchPlaneSide=SIDE1, origin=(0, 0, 0))
sk = myModel.ConstrainedSketch(name='Stringerprofile', 
    sheetSize=10000, gridSpacing=250, transform=tr)
#绘制第一条Stringer
leftpoint = (0,eachcenterleft)
rightpoint = (length,eachcenterleft)
sk.Line(leftpoint, rightpoint)
#阵列
sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=1, spacing1=107.703, 
    angle1=0.0, number2=Snum, spacing2=Spitch, angle2=90.0)
#形成Stringer
myPlatePart.PartitionFaceBySketch(sketchUpEdge=Upedge, faces=Upface, sketch=sk)

#为Stringer创建set
strcords = [0 for _ in range(Snum)]
i = 0
while (i<Snum):
    if(i==0):
        tempx = tol
        tempy = eachcenterleft
        tempz = 0
    else:
        tempx = tol
        tempy = eachcenterleft+i*Spitch
        tempz = 0
    strcords[i] = (tempx, tempy, tempz)
    i = i+1

Stringeredges = myPlatePart.edges.findAt(coordinates=strcords)
#提取palte中的线作为加强筋
#提取Stringers
#: Warning: Stringer created using a Set will not be associated with the Set.
#: If the Set is later updated to refer to different geometry, the stringer will not update
myPlatePart.Stringer(edges=(Stringeredges,), name='Stringers')
#myPlatePart.Set(name='Set-Stringers',Stringers=(Stringeredges,))
myPlatePart.Set(stringerEdges=(('Stringers', Stringeredges), ), name='Set-Stringers')




#输入与载荷垂直方向的加强筋Fr的参数  注意要float参数
t_fields = (('F_Height (mm)','10'),('F_UpWidth (mm)','8'),('F_BotWidth (mm)','8'),('F_Pitch (mm)','50'),('F_Number (mm)','10'),)
p_FHeight, p_FUpWidth, p_FBotWidth, p_FPitch, p_FNum = getInputs(fields=t_fields, label='Frame Dimension:', dialogTitle='Create Frame')
Fheight = float(p_FHeight)
Fupwidth = float(p_FUpWidth)
Fbotwidth = float(p_FBotWidth)
Fnum = int(p_FNum)
Fpitch = float(p_FPitch)


#绘制加强筋Frame
#计算palte边界到第一个Frame中心的距离
eachcenterright = (length-(Fnum-1)*Fpitch)/2

i = 0
while (i<Snum+1):
    if(i==0):
        Upedge = myPlatePart.edges.findAt((length,tol,0),)
        Upface = myPlatePart.faces.findAt((tol,tol,0),)
        tr = myPlatePart.MakeSketchTransform(sketchPlane=Upface, sketchUpEdge=Upedge, 
            sketchPlaneSide=SIDE1, origin=(0, 0, 0))
        sk = myModel.ConstrainedSketch(name='Frameprofile', 
            sheetSize=10000, gridSpacing=250, transform=tr)
        #绘制第一条Frame
        endpoint = (eachcenterright,0)
        toppoint = (eachcenterright,eachcenterleft)
        sk.Line(endpoint, toppoint)
        #阵列
        sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=Fnum, spacing1=Fpitch, 
            angle1=0.0, number2=1, spacing2=107.703, angle2=90.0)
        #形成Frame
        myPlatePart.PartitionFaceBySketch(sketchUpEdge=Upedge, faces=Upface, sketch=sk)
    elif(i==Snum):
        Upedge = myPlatePart.edges.findAt((length,width-tol,0),)
        Upface = myPlatePart.faces.findAt((tol,width-tol,0),)
        tr = myPlatePart.MakeSketchTransform(sketchPlane=Upface, sketchUpEdge=Upedge, 
            sketchPlaneSide=SIDE1, origin=(0, 0, 0))
        sk = myModel.ConstrainedSketch(name='Frameprofile', 
            sheetSize=10000, gridSpacing=250, transform=tr)
        #绘制第一条Frame
        endpoint = (eachcenterright,eachcenterleft+(i-1)*Spitch)
        toppoint = (eachcenterright,width)
        sk.Line(endpoint, toppoint)
        sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=Fnum, spacing1=Fpitch, 
            angle1=0.0, number2=1, spacing2=107.703, angle2=90.0)
        #阵列
        sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=Fnum, spacing1=Fpitch, 
            angle1=0.0, number2=1, spacing2=107.703, angle2=90.0)
        #形成Frame
        myPlatePart.PartitionFaceBySketch(sketchUpEdge=Upedge, faces=Upface, sketch=sk)
    else:
        Upedge = myPlatePart.edges.findAt((length,eachcenterleft+i*Spitch-tol,0),)
        Upface = myPlatePart.faces.findAt((tol,eachcenterleft+i*Spitch-tol,0),)
        tr = myPlatePart.MakeSketchTransform(sketchPlane=Upface, sketchUpEdge=Upedge, 
            sketchPlaneSide=SIDE1, origin=(0, 0, 0))
        sk = myModel.ConstrainedSketch(name='Frameprofile', 
            sheetSize=10000, gridSpacing=250, transform=tr)
        #绘制第一条Frame
        endpoint = (eachcenterright,eachcenterleft+(i-1)*Spitch)
        toppoint = (eachcenterright,eachcenterleft+i*Spitch)
        sk.Line(endpoint, toppoint)
        sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=Fnum, spacing1=Fpitch, 
            angle1=0.0, number2=1, spacing2=107.703, angle2=90.0)
        #阵列
        sk.linearPattern(geomList=sk.geometry.values(), vertexList=(), number1=Fnum, spacing1=Fpitch, 
            angle1=0.0, number2=1, spacing2=107.703, angle2=90.0)
        #形成Frame
        myPlatePart.PartitionFaceBySketch(sketchUpEdge=Upedge, faces=Upface, sketch=sk)
    i = i+1

#为Frame创建set:Set-Frame
strcords = [0 for _ in range(Snum+1)*Fnum]
i = 0
while (i<Snum+1):
    j = 0
    while (j<Fnum):
        if(i==0):
            tempx = eachcenterright+j*Fpitch
            tempy = eachcenterleft/2
            tempz = 0
        elif(i==Snum):
            tempx = eachcenterright+j*Fpitch
            tempy = width-tol
            tempz = 0
        else:
            tempx = eachcenterright+j*Fpitch
            tempy = eachcenterleft+i*Spitch-tol
            tempz = 0
        strcords[i*Fnum+j] = (tempx, tempy, tempz)
        j = j+1
    i = i+1

Frameedges = myPlatePart.edges.findAt(coordinates=strcords)
#提取palte中的线作为加强筋
#提取Frames
#: Warning: Stringer created using a Set will not be associated with the Set.
#: If the Set is later updated to refer to different geometry, the stringer will not update
myPlatePart.Stringer(edges=(Frameedges,), name='Frames')
#myPlatePart.Set(name='Set-Frames',Stringers=(Frameedges,))      不能用，属性会丢，要选stringer
myPlatePart.Set(stringerEdges=(('Frames', Frameedges), ), name='Set-Frames')




#导入Assembly模块
import assembly 

#创建实例部件
myAssembly = myModel.rootAssembly
myInstance = myAssembly.Instance(name='Stiffened_plate_shellbeam-1', part=myPlatePart, dependent=ON)

#导入step模块
import step 

#在初始分析步Initial之后创建一个分析步Buckle
myModel.BuckleStep(name='Buckle', 
    previous='Initial', numEigen=10, vectors=18)

#导入load模块
import load      # 888888888888888888

#通过坐标找到左右两个边界
#左边界Set-LeftEnd
strcords = [0 for _ in range(Snum+1)]
i = 0
while (i<Snum+1):
    if(i==0):
        tempx = 0
        tempy = tol
        tempz = 0
    elif(i==Snum):
        tempx = 0
        tempy = width-tol
        tempz = 0
    else:
        tempx = 0
        tempy = eachcenterleft+i*Spitch-tol
        tempz = 0
    strcords[i] = (tempx, tempy, tempz)
    i = i+1

Leftedges = myInstance.edges.findAt(coordinates=strcords)
myAssembly.Set(name='LeftEnds',edges=(Leftedges,))

#左边界Set-LeftEnd
strcords = [0 for _ in range(Snum+1)]
i = 0
while (i<Snum+1):
    if(i==0):
        tempx = length
        tempy = tol
        tempz = 0
    elif(i==Snum):
        tempx = length
        tempy = width-tol
        tempz = 0
    else:
        tempx = length
        tempy = eachcenterleft+i*Spitch-tol
        tempz = 0
    strcords[i] = (tempx, tempy, tempz)
    i = i+1

Rightedges = myInstance.edges.findAt(coordinates=strcords)
myAssembly.Set(name='RightEnds',edges=(Rightedges,))


#在左右两端创建固定约束
#在左端创建约束
#LeftRegion = myAssembly.set['LeftEnds']        # solid里可以用，shell不行？ AttributeError: 'Assembly' object has no attribute 'set'#
LeftRegion = regionToolset.Region(edges=Leftedges)
myModel.DisplacementBC(name='LeftEnds', 
    createStepName='Initial', region=LeftRegion, u1=UNSET, u2=SET, u3=SET, 
    ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, 
    fieldName='', localCsys=None)
#在右端创建约束
#RightRegion = myAssembly.sets['RightEnds']        
RightRegion = regionToolset.Region(edges=Rightedges)
myModel.DisplacementBC(name='RightEnds', 
    createStepName='Initial', region=RightRegion, u1=SET, u2=SET, u3=SET, ur1=UNSET, 
    ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, 
    fieldName='', localCsys=None)

#在左端施加载荷 
#换算载荷
load = 1*width*thickness/width
LeftRegion = regionToolset.Region(side1Edges=Leftedges)        #!!!!!不能不写这一行
myModel.ShellEdgeLoad(name='Axis-load', createStepName='Buckle', 
    region=LeftRegion, magnitude=load, distributionType=UNIFORM, field='', localCsys=None)

#导入mesh模块
import mesh 

#为Plate指定单元类型
Regions = myPlatePart.sets['Set-plate']
elemType1 = mesh.ElemType(elemCode=S4R, elemLibrary=STANDARD, 
    secondOrderAccuracy=OFF, hourglassControl=DEFAULT)
elemType2 = mesh.ElemType(elemCode=S3, elemLibrary=STANDARD)
myPlatePart.setElementType(regions=Regions, elemTypes=(elemType1, elemType2))
#elemType = mesh.ElemType(elemCode=C3D8R, elemLibrary=STANDARD)

#为Stringer指定单元类型
elemType1 = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)
Regions = myPlatePart.sets['Set-Stringers']
myPlatePart.setElementType(regions=Regions, elemTypes=(elemType1,))


#为Frames指定单元类型
elemType1 = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)
Regions = myPlatePart.sets['Set-Frames']
myPlatePart.setElementType(regions=Regions, elemTypes=(elemType1,))


#为零件整体撒种子
myPlatePart.seedPart(size=2 ,deviationFactor=0.1, minSizeFactor=0.1)

#为零件生成网格
myPlatePart.generateMesh()


#导入material模块
import material

stepindex = getInput('Enter the material type (1.Composite; 2.Metal):')
stepindex = int(stepindex)
if (stepindex==2):
    import material
    #创建金属材料
    mat_Matel = myModel.Material(name='Metal')
    #输入金属材料属性
    t_fields = (('Density(t/mm3)','1.6E-009'),('E(MPa)','200000'),('Nu','0.3'))
    m_Den, m_E, m_Nu = getInputs(fields=t_fields,label='Material parameter:', dialogTitle='Create Metal')
    mat_Density = float(m_Den)
    mat_E = float(m_E)
    mat_Nu = float(m_Nu)
    #定义材料属性
    mat_Density = 1.6E-009
    mat_E = 200000
    mat_Nu = 0.3
    #创建材料参数
    mat_Matel.Density(table=((mat_Density,),))
    isotropic = (mat_E,mat_Nu)
    mat_Matel.Elastic(type=ISOTROPIC, table=(isotropic,))
    #***********分割线
    #为Plate创建section        Regions = myPlatePart.sets['Set-plate']
    import section
    myModel.HomogeneousShellSection(name='Section-Plate', 
        preIntegrate=OFF, material='Metal', thicknessType=UNIFORM, 
        thickness=thickness, thicknessField='', idealization=NO_IDEALIZATION, 
        poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
        useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)
    Regions = myPlatePart.sets['Set-plate']
    myPlatePart.SectionAssignment(region=Regions, sectionName='Section-Plate', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='',thicknessAssignment=FROM_SECTION)
    #创建Stringer的截面形状
    myModel.TrapezoidalProfile(name='Profile-Stringer', a=Sbotwidth, b=Sheight, 
        c=Supwidth, d=-thickness)        
    #为Stringer创建beam_section
    myModel.BeamSection(name='Section-Stringer', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-Stringer', 
        material='Metal', temperatureVar=LINEAR, consistentMassMatrix=False)
    #赋予Stringer材料属性
    regions = myPlatePart.sets['Set-Stringers']
    myPlatePart.SectionAssignment(region=regions, sectionName='Section-Stringer', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    #创建Frame的截面形状
    myModel.TrapezoidalProfile(name='Profile-Frame', a=Fbotwidth, b=Fheight, 
        c=Fupwidth, d=-thickness)        
    #为Frame创建beam_section
    myModel.BeamSection(name='Section-Frame', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-Frame', 
        material='Metal', temperatureVar=LINEAR, consistentMassMatrix=False)
    #赋予Frame材料属性
    regions = myPlatePart.sets['Set-Frames']
    myPlatePart.SectionAssignment(region=regions, sectionName='Section-Frame', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    #赋予Stringer筋的方向n1            t方向为x轴正向   （n1，n2，t）符合右手系
    regions=myPlatePart.sets['Set-Stringers']
    myPlatePart.assignBeamSectionOrientation(region=regions, method=N1_COSINES, n1=(0.0, 1.0, 0.0))
    #赋予Frame筋的方向n1               t方向为y轴正向 
    regions=myPlatePart.sets['Set-Frames']
    myPlatePart.assignBeamSectionOrientation(region=regions, method=N1_COSINES, n1=(-1.0, 0.0, 0.0))
elif (stepindex==1):
    import material
    #创建复合材料
    mat_lam = myModel.Material(name='Laminate')
    #输入单层板材料参数(交互)
    t_fields = (('Density(t/mm3)','1.6E-009'),('E1(MPa)','155000'),('E2(MPa)','9420'),('E3(MPa)','9420'),
        ('Nu12','0.27'),('Nu13','0.27'),('Nu23','0.3'),('G12(MPa)','5400'),('G13(MPa)','5400'),('G23(MPa)','3900'))
    m_Den, m_E1, m_E2, m_E3, m_Nu12, m_Nu13, m_Nu23, m_G12, m_G13, m_G23 = getInputs(fields=t_fields,
        label='Material parameter:', dialogTitle='Create Laminate')
    mat_Density = float(m_Den)
    mat_E1 = float(m_E1)
    mat_E2 = float(m_E2)
    mat_E3 = float(m_E3)
    mat_Nu12 = float(m_Nu12)
    mat_Nu13 = float(m_Nu13)
    mat_Nu23 = float(m_Nu23)
    mat_G12 = float(m_G12)
    mat_G13 = float(m_G13)
    mat_G23 = float(m_G23)
    #定义材料属性
    mat_Density = 1.6E-009
    mat_E1 = 155000.0
    mat_E2 = 9420.0
    mat_E3 = 9420.0
    mat_Nu12 = 0.27
    mat_Nu13 = 0.27
    mat_Nu23 = 0.3
    mat_G12 = 5400
    mat_G13 = 5400
    mat_G23 = 3900
    #创建材料参数
    mat_lam.Density(table=((mat_Density,),))
    engineering_constants = (mat_E1,mat_E2,mat_E3,mat_Nu12,mat_Nu13,
        mat_Nu23,mat_G12,mat_G13,mat_G23)
    mat_lam.Elastic(type=ENGINEERING_CONSTANTS, table=(engineering_constants,))
    #创建复合材料梁Stringer等效材料属性
    mat_Strbeam = myModel.Material(name='Mat_Strbeam')
    #输入复合材料梁Stringer等效材料属性
    t_fields = (('Density(t/mm3)','1.6E-009'),('E1(MPa)','59228'),('E2(MPa)','59228'),('E3(MPa)','10168'),
        ('Nu12','0.304'),('Nu13','0.229'),('Nu23','0.229'),('G12(MPa)','22705'),('G13(MPa)','4529'),('G23(MPa)','4529'))
    s_Den, s_E1, s_E2, s_E3, s_Nu12, s_Nu13, s_Nu23, s_G12, s_G13, s_G23 = getInputs(fields=t_fields,
        label='Material parameter:', dialogTitle='Create Mat_Strbeam')
    mats_Density = float(s_Den)
    mats_E1 = float(s_E1)
    mats_E2 = float(s_E2)
    mats_E3 = float(s_E3)
    mats_Nu12 = float(s_Nu12)
    mats_Nu13 = float(s_Nu13)
    mats_Nu23 = float(s_Nu23)
    mats_G12 = float(s_G12)
    mats_G13 = float(s_G13)
    mats_G23 = float(s_G23)
    #定义材料属性
    mats_Density = 1.6E-009
    mats_E1 = 59228.0
    mats_E2 = 59228.0
    mats_E3 = 10168.0
    mats_Nu12 = 0.304
    mats_Nu13 = 0.229
    mats_Nu23 = 0.229
    mats_G12 = 22705
    mats_G13 = 4529
    mats_G23 = 4529
    #创建材料参数
    mat_Strbeam.Density(table=((mats_Density,),))
    engineering_constants = (mats_E1,mats_E2,mats_E3,mats_Nu12,mats_Nu13,
        mats_Nu23,mats_G12,mats_G13,mats_G23)
    mat_Strbeam.Elastic(type=ENGINEERING_CONSTANTS, table=(engineering_constants,))
    #创建复合材料梁Frame等效材料属性
    mat_Frabeam = myModel.Material(name='Mat_Frabeam')
    #输入复合材料梁Frame等效材料属性
    t_fields = (('Density(t/mm3)','1.6E-009'),('E1(MPa)','59228'),('E2(MPa)','59228'),('E3(MPa)','10168'),
        ('Nu12','0.304'),('Nu13','0.229'),('Nu23','0.229'),('G12(MPa)','22705'),('G13(MPa)','4529'),('G23(MPa)','4529'))
    f_Den, f_E1, f_E2, f_E3, f_Nu12, f_Nu13, f_Nu23, f_G12, f_G13, f_G23 = getInputs(fields=t_fields,
        label='Material parameter:', dialogTitle='Create Mat_Frabeam')
    matf_Density = float(f_Den)
    matf_E1 = float(f_E1)
    matf_E2 = float(f_E2)
    matf_E3 = float(f_E3)
    matf_Nu12 = float(f_Nu12)
    matf_Nu13 = float(f_Nu13)
    matf_Nu23 = float(f_Nu23)
    matf_G12 = float(f_G12)
    matf_G13 = float(f_G13)
    matf_G23 = float(f_G23)
    #定义材料属性
    matf_Density = 1.6E-009
    matf_E1 = 59228.0
    matf_E2 = 59228.0
    matf_E3 = 10168.0
    matf_Nu12 = 0.304
    matf_Nu13 = 0.229
    matf_Nu23 = 0.229
    matf_G12 = 22705
    matf_G13 = 4529
    matf_G23 = 4529
    #创建材料参数
    mat_Frabeam.Density(table=((matf_Density,),))
    engineering_constants = (matf_E1,matf_E2,matf_E3,matf_Nu12,matf_Nu13,
        matf_Nu23,matf_G12,matf_G13,matf_G23)
    mat_Frabeam.Elastic(type=ENGINEERING_CONSTANTS, table=(engineering_constants,))
    #***********分割线
    #***********分割线
    #创建复材section
    import section
    #建立直角坐标系       
    Layup = myPlatePart.DatumCsysByThreePoints(name='Layup',coordSysType=CARTESIAN,
        origin=(0,0,0),point1=(1,0,0),point2=(0,1,0))
    #创建plate铺层
    layupOrientation = myPlatePart.datums[Layup.id]
    compositeLayup = myPlatePart.CompositeLayup(name='plate', description='', elementType=SHELL, 
        symmetric=False, offsetType=BOTTOM_SURFACE, thicknessAssignment=FROM_SECTION)
    #***********分割线
    compositeLayup.ReferenceOrientation(orientationType=SYSTEM, 
        localCsys=layupOrientation, fieldName='', 
        additionalRotationType=ROTATION_NONE, angle=0.0, 
        additionalRotationField='', axis=AXIS_3, stackDirection=STACK_3)
    #***********分割线
    laythickness = 0.25
    layerangles = [0,45,90,-45,0,45,90,-45,-45,90,45,0,-45,90,45,0]
    totalLayerNum = ceil(thickness/laythickness)
    #***********分割线
    i = 0 
    tempNum = 0
    iterNum = (totalLayerNum)/len(layerangles)
    tempstr1 = 'Ply-'+str(tempNum)
    while (i<iterNum):
            i = i+1
            j = 0
            while (j<len(layerangles)):
                tempNum = (i-1)*len(layerangles)+j+1
                tempstr1 = 'Ply-'+str(tempNum)
                regions = myPlatePart.sets['Set-plate']
                compositeLayup.CompositePly(suppressed=False, plyName=tempstr1, region=regions, 
                material='Laminate', thicknessType=SPECIFY_THICKNESS, 
                thickness=laythickness, orientationType=SPECIFY_ORIENT, orientationValue=layerangles[j], 
                additionalRotationType=ROTATION_NONE, additionalRotationField='', 
                axis=AXIS_3, angle=0.0, numIntPoints=1)
                j = j+1
    #创建Stringer的截面形状
    myModel.TrapezoidalProfile(name='Profile-Stringer', a=Sbotwidth, b=Sheight, 
        c=Supwidth, d=-thickness)        
    #为Stringer创建beam_section
    myModel.BeamSection(name='Section-Stringer', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-Stringer', 
        material='Mat_Strbeam', temperatureVar=LINEAR, consistentMassMatrix=False)
    #赋予Stringer材料属性
    regions = myPlatePart.sets['Set-Stringers']
    myPlatePart.SectionAssignment(region=regions, sectionName='Section-Stringer', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    #创建Frame的截面形状
    myModel.TrapezoidalProfile(name='Profile-Frame', a=Fbotwidth, b=Fheight, 
        c=Fupwidth, d=-thickness)        
    #为Frame创建beam_section
    myModel.BeamSection(name='Section-Frame', 
        integration=DURING_ANALYSIS, poissonRatio=0.0, profile='Profile-Frame', 
        material='Mat_Frabeam', temperatureVar=LINEAR, consistentMassMatrix=False)
    #赋予Frame材料属性
    regions = myPlatePart.sets['Set-Frames']
    myPlatePart.SectionAssignment(region=regions, sectionName='Section-Frame', offset=0.0, 
        offsetType=BOTTOM_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
    #赋予Stringer筋的方向n1            t方向为x轴正向   （n1，n2，t）符合右手系
    regions=myPlatePart.sets['Set-Stringers']
    myPlatePart.assignBeamSectionOrientation(region=regions, method=N1_COSINES, n1=(0.0, 1.0, 0.0))
    #赋予Frame筋的方向n1               t方向为y轴正向 
    regions=myPlatePart.sets['Set-Frames']
    myPlatePart.assignBeamSectionOrientation(region=regions, method=N1_COSINES, n1=(-1.0, 0.0, 0.0))

#导入job模块
import job
#为模型创建并提交分析作业
jobName = 'Eq-stiffened-Plate-BuckleAnalysis'
myJob = mdb.Job(name=jobName, model = 'Stiffened_plate_shellbeam', description='Plate Static Analysis')
#myJob.submit()








