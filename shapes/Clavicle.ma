//Maya ASCII 2017 scene
//Name: Clavicle.ma
//Last modified: Fri, Jun 29, 2018 10:21:47 PM
//Codeset: 1252
requires maya "2017";
requires "stereoCamera" "10.0";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2017";
fileInfo "version" "2017";
fileInfo "cutIdentifier" "201608291545-1001872";
fileInfo "osv" "Microsoft Windows 8 Home Premium Edition, 64-bit  (Build 9200)\n";
createNode transform -n "Clavicle:Clavicle:Clavicle1:Clavicle1";
	rename -uid "8019D6C3-4B78-AE89-72BD-AC8240C5E61C";
createNode nurbsCurve -n "Clavicle:Clavicle:Clavicle1:ClavicleShape1" -p "Clavicle:Clavicle:Clavicle1:Clavicle1";
	rename -uid "33F29F5C-4ECA-BEE9-2E39-BEBFF4FD95D0";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 6 0 no 3
		7 0 1 2 3 4 5 6
		7
		0 0 0
		-19.470444247523314 -5.0048749781574768e-015 -19.470444247523332
		-23.398828181359857 -5.8771514367400522e-015 -15.542060313686791
		-24.040344946822962 -5.6517012262331975e-015 -20.55739779771606
		-20.557409582750303 -4.8783342193382646e-015 -24.040333161788716
		-15.542081526748266 -4.1326032298207601e-015 -23.398806968298381
		-19.470444247523314 -5.0048749781574768e-015 -19.470444247523332
		;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".msaa" yes;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderUtilityList1;
	setAttr -s 134 ".u";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".ren" -type "string" "arnold";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
select -ne :ikSystem;
	setAttr -s 4 ".sol";
// End of Clavicle.ma
