//Maya ASCII 2017ff04 scene
//Name: stretchy_ik.ma
//Last modified: Tue, Mar 27, 2018 04:40:39 PM
//Codeset: 1252
requires maya "2017ff04";
currentUnit -l centimeter -a degree -t ntsc;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "2017";
fileInfo "cutIdentifier" "201702071345-1015190";
fileInfo "osv" "Microsoft Windows 8 Enterprise Edition, 64-bit  (Build 9200)\n";
createNode transform -s -n "persp";
	rename -uid "358EBE4E-401B-3A00-B749-78AA525BEC8C";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -2.0763637408937758 15.305998343160603 -0.98256566507726117 ;
	setAttr ".r" -type "double3" -90.33835272960259 -13.400000000000018 -1.6347828686490522e-015 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "4055EDE4-42E5-F250-A921-45BDBDC1E8CD";
	setAttr -k off ".v" no;
	setAttr ".fcp" 100000;
	setAttr ".coi" 15.308534267069637;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
	setAttr ".ai_translator" -type "string" "perspective";
createNode transform -s -n "top";
	rename -uid "670C48DE-4878-8FB2-10E0-459219E553DF";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "A40BA807-49BF-8D6D-39E3-9E9D96BA0D84";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".fcp" 100000;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "front";
	rename -uid "618606FA-4F59-E97D-24E2-F6975FCEA571";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "700C7376-43A6-D1F1-0F4E-3D8590E7F0B4";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".fcp" 100000;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "side";
	rename -uid "10AB591B-4045-88AA-0DA0-839874727810";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "9237D371-4042-0903-CD9D-5196F0668B10";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".fcp" 100000;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode joint -n "joint1";
	rename -uid "03DA76C6-474F-04C6-F145-498EFC729548";
	setAttr ".t" -type "double3" -2.0027293771616139 0 -0.0045371515459584622 ;
	setAttr ".r" -type "double3" -4.7859914974036516e-005 -6.9241661305439539 0.00035632429509039075 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 6.8473487737748826 0 ;
	setAttr ".radi" 0.55234453129834948;
createNode joint -n "joint2" -p "joint1";
	rename -uid "8A1A1E11-4A78-4E28-5439-4A8017DFA832";
	addAttr -ci true -sn "xDist" -ln "xDist" -at "double";
	setAttr ".t" -type "double3" 2.0119942717680912 0 -3.6082248300317588e-016 ;
	setAttr ".r" -type "double3" 0 13.796773621670454 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -13.79730730520536 0 ;
	setAttr ".radi" 0.55275489742671047;
	setAttr ".xDist" 2.0119942717680912;
createNode joint -n "joint3" -p "joint2";
	rename -uid "EA853BF4-47DE-242B-FD01-0EAC14F2EA36";
	addAttr -ci true -sn "xDist" -ln "xDist" -at "double";
	setAttr ".t" -type "double3" 2.0199280169164018 0 -2.7755575615628914e-017 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 6.9499585314304708 0 ;
	setAttr ".radi" 0.55275489742671047;
	setAttr ".xDist" 2.0199280169164018;
createNode ikEffector -n "effector1" -p "joint2";
	rename -uid "E561B33A-4D0D-2305-3068-08936B21B760";
	setAttr ".v" no;
	setAttr ".hd" yes;
createNode ikHandle -n "ikHandle1";
	rename -uid "C036035F-450F-2F3E-AE78-6BB099FFC933";
	setAttr ".t" -type "double3" 2.0291892624056413 2.489177604256148e-005 0.0008873234266372613 ;
	setAttr ".pv" -type "double3" 0.0022670243791466094 -1.7385239795477667e-007 -1.9999987151496643 ;
	setAttr ".roc" yes;
createNode lightLinker -s -n "lightLinker1";
	rename -uid "4C5E601E-428B-4CF1-C7C0-9C86BC5E2EED";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "A22E6BC0-4ED5-1F92-1E61-E9B231395D4E";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "E67E9B42-4F5F-ADDE-66BC-C592A3BDB930";
createNode displayLayerManager -n "layerManager";
	rename -uid "B215EEF8-41B6-FFBC-B441-30B40CBEF61A";
createNode displayLayer -n "defaultLayer";
	rename -uid "DEA7079A-49B5-E533-5399-E6B71644A657";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "0E0A5C85-4A8D-0696-1828-74BA7D6E91AB";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "0033311A-49DE-0C09-B8DD-768740243E3E";
	setAttr ".g" yes;
createNode ikRPsolver -n "ikRPsolver";
	rename -uid "0B96808C-4318-9CEC-592F-91B7F90B521C";
createNode distanceBetween -n "distanceBetween1";
	rename -uid "D11036DD-4324-C7F4-1219-C3A9996A23C3";
createNode condition -n "condition1";
	rename -uid "3A3780A4-4AC2-67AE-06A0-C1A0CF7104A7";
	setAttr ".op" 2;
	setAttr ".st" 1;
createNode addDoubleLinear -n "addDoubleLinear1";
	rename -uid "6D37AB7A-4AA9-02C8-311F-09A9E378C471";
createNode multiplyDivide -n "multiplyDivide1";
	rename -uid "3B851F40-4219-BF4E-0E45-CAA4DBC40B12";
	setAttr ".op" 2;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "153FC17B-4ED7-D84E-C3F0-6D8E2D246EA8";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "E5D5EF7C-4C52-27EF-9FC2-18B3B9155F19";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" 2837.6889228209884 -2440.7702510911786 ;
	setAttr ".tgi[0].vh" -type "double2" 5724.6291805067758 -991.34766810872668 ;
	setAttr -s 9 ".tgi[0].ni";
	setAttr ".tgi[0].ni[0].x" 2622.857177734375;
	setAttr ".tgi[0].ni[0].y" -1350;
	setAttr ".tgi[0].ni[0].nvs" 18304;
	setAttr ".tgi[0].ni[1].x" 2315.71435546875;
	setAttr ".tgi[0].ni[1].y" -1321.4285888671875;
	setAttr ".tgi[0].ni[1].nvs" 18304;
	setAttr ".tgi[0].ni[2].x" 4158.5712890625;
	setAttr ".tgi[0].ni[2].y" -1517.142822265625;
	setAttr ".tgi[0].ni[2].nvs" 18304;
	setAttr ".tgi[0].ni[3].x" 3851.428466796875;
	setAttr ".tgi[0].ni[3].y" -1560;
	setAttr ".tgi[0].ni[3].nvs" 18304;
	setAttr ".tgi[0].ni[4].x" 4772.85693359375;
	setAttr ".tgi[0].ni[4].y" -1712.857177734375;
	setAttr ".tgi[0].ni[4].nvs" 18304;
	setAttr ".tgi[0].ni[5].x" 3237.142822265625;
	setAttr ".tgi[0].ni[5].y" -1472.857177734375;
	setAttr ".tgi[0].ni[5].nvs" 18304;
	setAttr ".tgi[0].ni[6].x" 3544.28564453125;
	setAttr ".tgi[0].ni[6].y" -1517.142822265625;
	setAttr ".tgi[0].ni[6].nvs" 18304;
	setAttr ".tgi[0].ni[7].x" 2930;
	setAttr ".tgi[0].ni[7].y" -1380;
	setAttr ".tgi[0].ni[7].nvs" 18304;
	setAttr ".tgi[0].ni[8].x" 4465.71435546875;
	setAttr ".tgi[0].ni[8].y" -1798.5714111328125;
	setAttr ".tgi[0].ni[8].nvs" 18304;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 4 ".u";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".ren" -type "string" "arnold";
	setAttr ".fs" 1;
	setAttr ".ef" 10;
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
connectAttr "condition1.ocr" "joint1.sx";
connectAttr "joint1.s" "joint2.is";
connectAttr "condition1.ocr" "joint2.sx";
connectAttr "joint2.s" "joint3.is";
connectAttr "joint3.tx" "effector1.tx";
connectAttr "joint3.ty" "effector1.ty";
connectAttr "joint3.tz" "effector1.tz";
connectAttr "joint1.msg" "ikHandle1.hsj";
connectAttr "effector1.hp" "ikHandle1.hee";
connectAttr "ikRPsolver.msg" "ikHandle1.hsv";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "joint1.wm" "distanceBetween1.im1";
connectAttr "ikHandle1.wm" "distanceBetween1.im2";
connectAttr "multiplyDivide1.ox" "condition1.ft";
connectAttr "multiplyDivide1.ox" "condition1.ctr";
connectAttr "joint3.xDist" "addDoubleLinear1.i1";
connectAttr "joint2.xDist" "addDoubleLinear1.i2";
connectAttr "distanceBetween1.d" "multiplyDivide1.i1x";
connectAttr "addDoubleLinear1.o" "multiplyDivide1.i2x";
connectAttr "distanceBetween1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[0].dn"
		;
connectAttr "ikHandle1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[1].dn";
connectAttr "joint3.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[2].dn";
connectAttr "joint2.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[3].dn";
connectAttr ":defaultRenderUtilityList1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[4].dn"
		;
connectAttr "condition1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[5].dn";
connectAttr "joint1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[6].dn";
connectAttr "multiplyDivide1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[7].dn";
connectAttr "addDoubleLinear1.msg" "MayaNodeEditorSavedTabsInfo.tgi[0].ni[8].dn"
		;
connectAttr "distanceBetween1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "condition1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "addDoubleLinear1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "multiplyDivide1.msg" ":defaultRenderUtilityList1.u" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "ikRPsolver.msg" ":ikSystem.sol" -na;
// End of stretchy_ik.ma
