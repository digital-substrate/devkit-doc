Raptor Editor
=============

.. rubric:: Files: 20 | Namespace: Raptor | Pattern: Single-attachment (translated from C++ codebase)

3D visualization data model for Raptor Editor.

Overview
--------

Raptor Editor is a **comprehensive 3D visualization data model**, demonstrating modeling at
realistic scale — many concepts, deep type structures, monolithic attachments. This DSM
defines the complete data model for:

- **Scene composition**: Models, Surfaces, Geometry Layers, Position Layers
- **Materials**: Multi-layer shading (diffuse, specular, illumination), PBR materials, car
  paint (AxF)
- **Lighting**: Spot lights, area lights, directional lights, HDR environments
- **Camera**: Perspective/orthographic, depth of field, motion blur
- **Animation**: Timelines, keyframes, Bezier camera paths, kinematics

.. note::

   **Single-attachment pattern**: This model uses **one attachment per concept** (named
   ``properties``). It was translated directly from an existing C++ codebase, where data
   structures already had this monolithic form. This demonstrates that DSM can adapt to
   an existing codebase. For new projects, the recommended pattern
   (see :doc:`graph_editor`) uses **multiple attachments per concept** to separate concerns.

----

Pool_Surfaces.dsm
-----------------

**Domain:** Pool: ModelSurface

Minimal function pool for **material assignment**. In Raptor, surfaces are 3D geometry
that can have different materials per AspectLayer (e.g., "showroom" vs "outdoor" lighting
scenarios).

The single function ``assign_material`` links a Surface to a Material within a specific
AspectLayer context - enabling the same model to render with different material
configurations.

.. code-block:: dsm

   """This pool is dedicated to Surface"""
   attachment_function_pool ModelSurface {fd61d936-d350-4a18-a2ca-cc7d7d3a9dc6} {

   """assign a material to a surface"""
   mutable void assign_material(key<AspectLayer> layerKey, key<Surface> surfaceKey, key<Material> materialKey);

   };

----

Pool_Tools.dsm
--------------

**Domain:** Pool: Tools

Pure utility **function_pool**. Provides helper functions for testing and UI:

- ``randomColor``, ``randomWord`` - test data generation
- ``userName`` - current user for metadata
- ``add``, ``isEven`` - basic arithmetic demos

.. code-block:: dsm

   """This pool provides access to the various utility functions."""
   function_pool Tools {ac3b7779-e0bf-46f8-95a1-bcf1df164022} {

   """Return a + b."""
   int64 add(int64 a, int64 b);

   """Return true if a is even."""
   bool isEven(int64 a);

   """Return a random color."""
   Vector randomColor();

   """Return a random word."""
   string randomWord();

   """Return the current user name."""
   string userName();

   };

----

Raptor_BezierPath.dsm
---------------------

**Domain:** BezierPath

Defines **smooth camera paths** for cinematic animations. A BezierPath is a spline curve
that cameras can follow during timeline playback.

Structure
^^^^^^^^^

- ``BezierPathProperties``: name, color (for viewport display), vertices list
- ``BezierPathVertex``: control point with ``leftTangent`` and ``rightTangent`` for smooth
  interpolation
- ``isClosed``: loop the path or stop at end
- ``invertEvaluationDirection``: reverse camera travel direction

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept BezierPath;

   struct BezierPathProperties {
       string name = "BezierPath";
       Vector color = {1.0, 1.0, 1.0};
       float startAbscissa;
       bool invertEvaluationDirection;
       bool isClosed;
       vector<BezierPathVertex> vertices;
   };

   struct BezierPathVertex {
       Vector point;
       Vector leftTangent;
       Vector rightTangent;
       bool areTangentLinkedToPoint;
       bool areTangentLinked;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<BezierPath, BezierPathProperties> properties;

   };

----

Raptor_Camera.dsm
-----------------

**Domain:** Camera

Defines the **virtual camera** for rendering. Cameras capture the scene from a specific
viewpoint with realistic optical properties.

Key Properties
^^^^^^^^^^^^^^

- ``PointOfView``: position, target, up vector (defines view matrix)
- ``CameraOpticalProperties``: focal length, sensor size, depth of field, aperture
- ``CameraProjection``: perspective vs orthographic
- ``lensShiftProperties``: tilt-shift photography simulation (architecture rendering)

.. note::

   Camera has TWO attachments (``properties`` + ``lensShiftProperties``) - a deviation
   from the strict single-attachment pattern, showing that even translated models
   sometimes need multiple attachments for optional features.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Camera;

   struct CameraProperties {
       string name = "Camera";
       PointOfView pointOfView;
       CameraOpticalProperties opticalProperties;
       optional<key<Sensor>> sensorKey;
       bool exposedInConfiguration = true;
   };

   struct CameraDepthOfField {
       bool enabled;
       float aperture;
       int32 sampleCount = 32;
   };

   struct CameraDepthRange {
       CameraDepthRangePolicy policy = .lookAtPointBasedInterest;
       float zNear = 0.1;
       float zFar = 100.0;
   };

   enum CameraDepthRangePolicy {
       frustumBased,
       fixedDepthRange,
       lookAtPointBasedInterest,
       useGlobalPolicy
   };

   enum CameraFovType {
       x,
       y
   };

   struct CameraMotionBlur {
       bool enabled;
       bool objectMotionBlur;
       float simulatedFps = 24.0;
   };

   struct CameraOpticalProperties {
       CameraFovType fovType = .y;
       float fov = 0.785398;
       CameraOrientation orientation;
       CameraDepthOfField depthOfField;
       CameraMotionBlur motionBlur;
       CameraDepthRange depthRange;
   };

   enum CameraOrientation {
       landscape,
       portrait
   };

   struct LensShiftProperties {
       float lensShiftX;
       float lensShiftY;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Camera, CameraProperties> properties;
   attachment<Camera, LensShiftProperties> lensShiftProperties;

   };

----

Raptor_ClippingPlane.dsm
------------------------

**Domain:** ClippingPlaneGroup

Defines clipping planes for sectional views of 3D models.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept ClippingPlaneGroup;
   struct ClippingPlaneGroupProperties {
       vector<ClippingPlaneGroupPlane> planes;
       bool isClippingEnabled;
       ClippingPlaneGroupBackfaceCullPolicy backfaceCullPolicy;
       bool isSurfaceTagsEnabled;
       set<string> surfaceTags;
   };

   enum ClippingPlaneGroupBackfaceCullPolicy {
       never,
       always,
       surface
   };

   struct ClippingPlaneGroupPlane {
       bool enabled;
       bool invertNormalDirection;
       ClippingPlaneGroupVisualization visualisation;
       ClippingPlaneGroupSlice slice;
       Transform transform;
   };

   struct ClippingPlaneGroupSlice {
       bool enabled = true;
       Vector color = {1.0, 0.0, 0.0};
       float thickness = 0.005;
   };

   struct ClippingPlaneGroupVisualization {
       bool planeEnabled;
       float planeWidth = 1.0;
       float planeHeight = 1.0;
       float planeAlpha = 0.1;
       Vector planeColor = {1.0, 0.0, 0.0};
       bool gridEnabled;
       float gridStep = 0.1;
       Vector gridColor = {1.0, 0.0, 0.0};
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<ClippingPlaneGroup, ClippingPlaneGroupProperties> properties;

   };

----

Raptor_Configuration.dsm
------------------------

**Domain:** ConfigurationExpression, ConfigurationRule

Defines configuration rules for product variants (e.g., car with/without sunroof).

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   struct ConfigurationExpressionProperties {
       ConfigurationExpressionOperationType operationType;
       optional<key<ConfigurationExpression>> leftExpressionKey;
       optional<key<ConfigurationExpression>> rightExpressionKey;
       string symbol;
   };

   concept ConfigurationExpression;

   enum ConfigurationExpressionOperationType {
       defined,
       and,
       or,
       xor,
       not
   };

   club ConfigurationTargetSource;
   membership ConfigurationTargetSource Model;
   membership ConfigurationTargetSource Product;
   membership ConfigurationTargetSource Overlay;

   club ConfigurationTargetElement;
   membership ConfigurationTargetElement GeometryLayer;
   membership ConfigurationTargetElement AspectLayer;
   membership ConfigurationTargetElement PositionLayer;
   membership ConfigurationTargetElement EnvironmentLayer;
   membership ConfigurationTargetElement LightingLayer;
   membership ConfigurationTargetElement LightingLayerColorLayer;
   membership ConfigurationTargetElement OverlayLayer;

   struct ConfigurationTarget {
       string name = "ConfigurationTarget";
       bool enabled;
       key<ConfigurationTargetSource> sourceKey;
       key<ConfigurationTargetElement> elementKey;
   };

   concept ConfigurationRule;
   struct ConfigurationRuleProperties {
       string name = "ConfigurationRule";
       bool enabled = true;
       key<ConfigurationExpression> expressionKey;
       vector<ConfigurationTarget> targets;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<ConfigurationExpression, ConfigurationExpressionProperties> properties;
   attachment<ConfigurationRule, ConfigurationRuleProperties> properties;

   };

----

Raptor_Environment.dsm
----------------------

**Domain:** Environment, EnvironmentGenerator, EnvironmentGeneratorHdrls, EnvironmentGeneratorLocal

Defines HDR environment lighting with support for HDRI files and local environment probes.

.. code-block:: dsm

   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Environment;
   struct EnvironmentProperties {
       string name = "Environment";
       optional<key<Thumbnail>> thumbnailKey;
       optional<key<EnvironmentGenerator>> generatorKey;
       float gamma = 1.0;
       float saturation;
       float diffuseExposure;
       float diffuseColoration;
       float specularExposure;
       float backgroundExposure;
       float backgroundGamma = 1.0;
       Vector position;
       Transform defaultTransform;
       EnvironmentParallaxCorrection parallaxCorrection;
       key<TextureCube> diffuseCubeKey;
       vector<key<TextureCube>> specularCubeKeys;
       optional<key<Texture>> backgroundTextureKey;
       vector<EnvironmentLight> environmentLights;
   };

   concept EnvironmentGenerator;

   concept EnvironmentGeneratorHdrls is a EnvironmentGenerator;
   struct EnvironmentGeneratorHdrlsProperties {
       bool immediateDataProcessing;
       int32 width;
       int32 height;
       blob_id data;
   };

   concept EnvironmentGeneratorLocal is a EnvironmentGenerator;
   struct EnvironmentGeneratorLocalProperties {
       key<Product> productKey;
       float radius = 1.0;
       int32 resolution;
       set<string> surfaceTags;
       bool rebuildOnConfig;
   };

   concept EnvironmentLayer;
   struct EnvironmentLayerProperties {
       string name = "EnvironmentLayer";
       bool enabled = true;
       map<key<Surface>, key<Environment>> environmentAssignments;
       map<key<Surface>, Transform> orientationAssignments;
   };

   struct EnvironmentLight {
       Vector direction;
       Vector color;
       float size;
   };

   struct EnvironmentParallaxCorrection {
       EnvironmentParallaxType parallaxType;
       Aabb aabb;
       Vector hemisphereCenter;
       float hemisphereRadius = 1.0;
       optional<key<Surface>> surfaceKey;
   };

   enum EnvironmentParallaxType {
       none,
       aabb,
       hemisphere,
       mesh
   };

   struct EnvironmentRenderProperties {
       bool hasEnvironmentOrientation;
       Vector environmentOrientation;
       bool hasSunPosition;
       Vector sunPosition;
       bool overrideSun;
       EnvironmentSunProperties sunProperties;
   };

   struct EnvironmentSunProperties {
       bool enabled;
       Vector color;
       float intensity = 1.0;
       float shadowIntensity = 0.1;
       bool isSpecularEnabled;
       float specularIntensity;
       float lightmapIntensity;
   };

   struct SunAuthoringProperties {
       bool enabled;
       bool enabledShadowsInMirrors;
       Vector color = {1.0, 1.0, 1.0};
       float intensity = 1.0;
       float shadowIntensity;
       float lightmapIntensity = 1.0;
       SunShadowQuality shadowQuality;
       SunShadowSmoothness shadowSmoothness;
       bool isSpecularEnabled = true;
       float specularIntensity = 1.0;
       float northOrientation;
       SunOrientationType orientationType;
       SunAuthoringManualOrientation manualOrientation;
       SunAuthoringTimeAndLocationOrientation timeAndLocationOrientation;
   };

   struct SunAuthoringManualOrientation {
       float azimuth;
       float altitude = 30.0;
   };

   struct SunAuthoringTimeAndLocationOrientation {
       int32 year = 2000;
       uint8 month = 1;
       uint8 day = 1;
       uint8 hour = 12;
       uint8 minute;
       uint8 second;
       float timezone = 1.0;
       bool daylightSaving = true;
       int32 daylightSavingMinutes = 60;
       float latitude = 44.8386;
       float longitude = 0.5783;
   };

   enum SunShadowQuality {
       veryLow,
       low,
       medium,
       fine,
       ultra
   };

   enum SunShadowSmoothness {
       none,
       weak,
       normal,
       fine,
       ultraFine,
       max
   };

   enum SunOrientationType {
       manual,
       timeAndLocation,
       extractedFromEnvironment
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Environment, EnvironmentProperties> properties;
   attachment<EnvironmentGeneratorHdrls, EnvironmentGeneratorHdrlsProperties> properties;
   attachment<EnvironmentGeneratorLocal, EnvironmentGeneratorLocalProperties> properties;
   attachment<EnvironmentLayer, EnvironmentLayerProperties> properties;

   };

----

Raptor_Iray.dsm
---------------

**Domain:** IraySettings, IrayMaterial, IrayMdlMaterial, IrayAxfMaterial

NVIDIA Iray path-tracing renderer integration with MDL materials and X-Rite AxF measured materials.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept IraySettings;
   struct IraySettingsProperties {
       float maxQuality = 0.99;
       uint32 maxSamples = 512;
       float maxRenderTime = 3600.0;
       uint32 maxPathLength = 12;
       float environmentExposure = 1.0;
       bool causticSampler;
       bool architecturalSampler;
       bool environmentMaterialEnabled;
       bool environmentMaterialUseAlternative;
       bool environmentBackgroundMode = true;
       IrayGround ground;
       IrayTonemapper tonemapper;
       IrayCameraEffects cameraEffects;
       bool firefliesFilteringEnabled;
       IrayDegrainFiltering degrain;
       IrayDenoiseFiltering denoise;
       IraySunSky sunSky;
   };

   struct IrayGround {
       bool enabled;
       float altitude;
       float shadowIntensity = 1.0;
       float scale = 1.5;
       float glossiness;
       Vector reflectivity = {1.0, 1.0, 1.0};
   };

   struct IrayTonemapper {
       bool enabled = true;
       IrayTonemappingMode mode;
       float burn = 0.2;
       float crush = 0.25;
       float ev = 7.0;
       float shutter = 0.125;
       float fNumber = 8.0;
       float filmIso = 100.0;
       float cm2Factor = 10.0;
       float saturation = 1.0;
       Vector whitePoint = {1.04287, 0.983863, 1.03358};
   };

   enum IrayTonemappingMode {
       standard,
       photographic
   };

   struct IrayCameraEffects {
       bool bloomEnabled;
       float bloomRadius = 0.01;
       float bloomThreshold = 0.9;
       float bloomBrightnessScale = 1.0;
       float vignetting;
   };

   struct IrayDegrainFiltering {
       bool enabled;
       IrayDegrainMode mode;
       int32 radius = 3;
       float blurDifference = 0.05;
   };

   enum IrayDegrainMode {
       pixelClipping,
       smartMedian,
       smartAverage,
       limitedBlur,
       limitedAutoBlur
   };

   struct IrayDenoiseFiltering {
       bool enabled;
       uint32 minIterations = 8;
       uint32 maxMemory = 2048;
       bool denoiseAlpha;
   };

   struct IraySunSky {
       bool enabled;
       float multiplier = 0.09;
       Vector rgbUnitConversion = {0.000666667, 0.000666667, 0.000666667};
       float haze = 0.5;
       float redblueShift;
       float saturation = 0.5;
       float horizonHeight = 0.001;
       float horizonBlur = 0.1;
       Vector groundColor = {0.4, 0.4, 0.4};
       Vector nightColor;
       float sunDiskIntensity = 0.01;
       float sunDiskScale = 0.5;
       float sunGlowIntensity = 1.0;
       bool physicallyScaledSun = true;
   };

   struct IrayLight {
       float intensity = 1.0;
       float exponent = 1.0;
       bool useAsPortal;
       bool useRadiantExitance;
   };

   concept IrayMaterial;
   struct IrayMaterialSettings {
       key<IrayMaterial> materialKey;
   };

   concept IrayMdlMaterial is a IrayMaterial;
   struct IrayMdlMaterialProperties {
       string name = "MdlMaterial";
       blob_id mdlData;
   };

   concept IrayAxfMaterial is a IrayMaterial;
   struct IrayAxfMaterialProperties {
       blob_id axfData;
   };

   concept IrayStdMaterial is a IrayMaterial;
   struct IrayStdMaterialProperties {
       float shadowIntensity;
   };

   concept IrayMatteMaterial is a IrayMaterial;
   struct IrayMatteMaterialProperties {
       float shadowIntensity;
       Vector color;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<IraySettings, IraySettingsProperties> properties;

   attachment<Light, IrayLight> iraySettings;
   attachment<Material, IrayMaterialSettings> iraySettings;

   attachment<IrayMdlMaterial, IrayMdlMaterialProperties> properties;
   attachment<IrayAxfMaterial, IrayAxfMaterialProperties> properties;
   attachment<IrayStdMaterial, IrayStdMaterialProperties> properties;
   attachment<IrayMatteMaterial, IrayMatteMaterialProperties> properties;

   };

----

Raptor_Kinematics.dsm
---------------------

**Domain:** Kinematics, KinematicsNode, KinematicsNodeAxis, KinematicsNodeNull

Defines articulated motion for mechanical assemblies (doors, wheels, robotic arms).

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   club KinematicsElement;
   membership KinematicsElement Surface;
   membership KinematicsElement BezierPath;
   membership KinematicsElement KinematicsNodeAxis;
   membership KinematicsElement KinematicsNodeNull;
   membership KinematicsElement KinematicsNodeVector;

   concept Kinematics;
   struct KinematicsProperties {
       vector<key<KinematicsNode>> nodeKeys;
       map<key<KinematicsElement>, vector<key<KinematicsConstraint>>> constraints;
       map<key<KinematicsElement>, key<KinematicsElement>> parents;
   };

   concept KinematicsNode;

   concept KinematicsNodeAxis is a KinematicsNode;
   struct KinematicsNodeAxisProperties {
       string name = "KinematicsNodeAxis";
       float minAngle;
       float maxAngle;
   };

   concept KinematicsNodeNull is a KinematicsNode;
   struct KinematicsNodeNullProperties {
       string name = "KinematicsNodeNull";
       vector<string> tags;
   };

   concept KinematicsNodeVector is a KinematicsNode;
   struct KinematicsNodeVectorProperties {
       string name = "KinematicsNodeVector";
       float minDistance;
       float maxDistance;
   };

   concept KinematicsConstraint;

   enum KinematicsConstraintAxis {
       x,
       y,
       z
   };

   concept KinematicsConstraintCopyOrientation is a KinematicsConstraint;
   struct KinematicsConstraintCopyOrientationProperties {
       key<KinematicsElement> targetKey;
       Vector offset;
   };

   concept KinematicsConstraintCopyPosition is a KinematicsConstraint;
   struct KinematicsConstraintCopyPositionProperties {
       key<KinematicsElement> targetKey;
       Vector offset;
   };

   concept KinematicsConstraintFollowPath is a KinematicsConstraint;
   struct KinematicsConstraintFollowPathProperties {
       key<KinematicsElement> targetKey;
       bool followCurve;
       KinematicsConstraintAxis followAimAxis;
       KinematicsConstraintAxis followUpAxis = .y;
       float curvilinearAbscissa = 0.0;
   };

   concept KinematicsConstraintLookAt is a KinematicsConstraint;
   struct KinematicsConstraintLookAtProperties {
       key<KinematicsElement> targetKey;
       KinematicsConstraintAxis aimAxis;
       KinematicsConstraintAxis upAxis = .y;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Kinematics, KinematicsProperties> properties;
   attachment<KinematicsNodeAxis, KinematicsNodeAxisProperties> properties;
   attachment<KinematicsNodeNull, KinematicsNodeNullProperties> properties;
   attachment<KinematicsNodeVector, KinematicsNodeVectorProperties> properties;
   attachment<KinematicsConstraintCopyOrientation, KinematicsConstraintCopyOrientationProperties> properties;
   attachment<KinematicsConstraintCopyPosition, KinematicsConstraintCopyPositionProperties> properties;
   attachment<KinematicsConstraintFollowPath, KinematicsConstraintFollowPathProperties> properties;
   attachment<KinematicsConstraintLookAt, KinematicsConstraintLookAtProperties> properties;

   };

----

Raptor_Library.dsm
------------------

**Domain:** Library, CameraGroup, MaterialGroup, BackgroundGroup

Defines the **asset library system** - reusable presets organized in folders.

Library Groups
^^^^^^^^^^^^^^

Each group is a folder concept:

- ``Library``: root container for all asset groups
- ``CameraGroup``: saved camera presets (viewpoints)
- ``MaterialGroup``: material presets
- ``BackgroundGroup``: background/environment presets
- ``EnvironmentGroup``: HDR environment presets
- ``LightGroup``: lighting presets
- ``SensorGroup``: render settings presets
- ``Folder``: generic subfolder for organization

Each group contains a ``vector<key<...>>`` of its items plus child folders, enabling nested
organization like a file system.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Library;
   struct LibraryProperties {
       key<CameraGroup> rootCameraGroupKey;
       key<MaterialGroup> rootMaterialGroupKey;
       key<Folder> rootTextureGroupKey;
       key<BackgroundGroup> rootBackgroundGroupKey;
       key<OverlayGroup> rootOverlayGroupKey;
       key<PostProcessGroup> rootPostprocessGroupKey;
       key<SensorGroup> rootSensorGroupKey;
       vector<key<ConfigurationRule>> configurationRuleKeys;
       map<key<Product>, vector<key<Camera>>> productCameras;
   };

   concept CameraGroup;
   struct CameraGroupProperties {
       string name = "Camera Group";
       vector<key<CameraGroup>> groupKeys;
       vector<key<Camera>> cameraKeys;
   };

   concept MaterialGroup;
   struct MaterialGroupProperties {
       string name = "Material Group";
       vector<key<MaterialGroup>> groupKeys;
       vector<key<Material>> materialKeys;
   };

   concept BackgroundGroup;
   struct BackgroundGroupProperties {
       string name = "Background Group";
       vector<key<BackgroundGroup>> groupKeys;
       vector<key<Background>> backgroundKeys;
   };

   concept OverlayGroup;
   struct OverlayGroupProperties {
       string name = "Overlay Group";
       vector<key<OverlayGroup>> groupKeys;
       vector<key<Overlay>> overlayKeys;
   };

   concept PostProcessGroup;
   struct PostProcessGroupProperties {
       string name = "PostProcess Group";
       vector<key<PostProcessGroup>> groupKeys;
       vector<key<PostProcess>> postProcessKeys;
   };

   concept SensorGroup;
   struct SensorGroupProperties {
       string name = "Sensor Group";
       vector<key<SensorGroup>> groupKeys;
       vector<key<Sensor>> sensorKeys;
   };

   concept Folder;
   struct FolderProperties {
       string name = "Folder";
       vector<key<Folder>> folderKeys;
       vector<uuid> entries;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Library, LibraryProperties> properties;

   attachment<CameraGroup, CameraGroupProperties> properties;
   attachment<MaterialGroup, MaterialGroupProperties> properties;
   attachment<BackgroundGroup, BackgroundGroupProperties> properties;
   attachment<OverlayGroup, OverlayGroupProperties> properties;
   attachment<PostProcessGroup, PostProcessGroupProperties> properties;
   attachment<SensorGroup, SensorGroupProperties> properties;

   attachment<Folder, FolderProperties> properties;

   };

----

Raptor_Lighting.dsm
-------------------

**Domain:** LightingLayer, LightingLayerColorLayer, Light, LightSpot

Defines the **lighting system** for realistic illumination. Lights are organized in
``LightingLayer`` groups that can be toggled independently.

Light Hierarchy
^^^^^^^^^^^^^^^

Concept inheritance via ``is a``:

- ``Light`` (abstract base)
    - ``LightSpot`` - cone-shaped spotlight with falloff
    - ``LightOmni`` - point light (omnidirectional)
    - ``LightSun`` - infinite directional light (outdoor scenes)
    - ``LightSky`` - ambient sky dome lighting
    - ``LightAreaPlane`` - soft rectangular light (studio softbox)
    - ``LightAreaCylinder`` - tubular light (fluorescent)
    - ``LightAreaMesh`` - light emitted from arbitrary geometry

Organization
^^^^^^^^^^^^

- ``LightingLayer``: groups lights that can be enabled/disabled together
- ``LightingLayerColorLayer``: color grading per lighting layer
- Multiple LightingLayers per Model allow A/B lighting comparison

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept LightingLayer;
   struct LightingLayerProperties {
       string name = "LightingLayer";
       bool enabled;
       float exposure = 1.0;
       float gamma = 1.0;
       vector<key<LightingLayerColorLayer>> colorLayerKeys;
       vector<key<Light>> lightKeys;
   };

   concept LightingLayerColorLayer;
   struct LightingLayerColorLayerProperties {
       string name = "LightingLayerColorLayer";
       bool enabled;
       float intensity = 1.0;
       Vector color = {1.0, 1.0, 1.0};
   };

   concept Light;
   struct LightProperties {
       string name;
       bool enabled = true;
       Vector color = {1.0, 1.0, 1.0};
       float intensity = 1.0;
       Vector position = {0.0, 0.1, 0.0};
       Vector orientation;
   };

   concept LightSpot is a Light;
   struct LightSpotProperties {
       float diameter = 0.05;
       Vector target = {0.0, 0.0, 1.0};
       float falloff = 45.0;
       float hotSpot = 43.0;
       LightShadow shadow;
       LightAttenuation attenuation;
       IESProfile iesProfile;
   };

   concept LightOmni is a Light;
   struct LightOmniProperties {
       float diameter = 0.05;
       LightShadow shadow;
       LightAttenuation attenuation;
       IESProfile iesProfile;
   };

   concept LightSun is a Light;
   struct LightSunProperties {
       float diameter = 0.05;
       LightShadow shadow;
   };

   concept LightSky is a Light;
   struct LightSkyProperties {
       float topAngle = 0.05;
       float bottomAngle = 0.05;
       optional<key<Environment>> environmentKey;
       LightShadow shadow;
   };

   concept LightAreaPlane is a Light;
   struct LightAreaPlaneProperties {
       float width = 1.0;
       float height = 1.0;
       LightShadow shadow;
       LightAttenuation attenuation;
       IESProfile iesProfile;
   };

   concept LightAreaCylinder is a Light;
   struct LightAreaCylinderProperties {
       float diameter = 0.2;
       float length = 1.0;
       LightShadow shadow;
       LightAttenuation attenuation;
       IESProfile iesProfile;
   };

   concept LightAreaMesh is a Light;
   struct LightAreaMeshProperties {
       key<Surface> surfaceKey;
       LightShadow shadow;
       LightAttenuation attenuation;
       IESProfile iesProfile;
   };

   struct LightShadow {
       bool cast = true;
       float intensity = 0.1;
       ShadowIntegrity integrity = .normal;
   };

   struct LightAttenuation {
       LightAttenuationType attenuationType = .physical;
       bool bounded;
       float fullEffect = 2.0;
       float falloff = 2.1;
   };

   struct IESProfile {
       bool enabled;
       blob_id data;
       Vector orientation = {-90.0, 0.0, 0.0};
   };

   enum ShadowIntegrity {
       weak,
       normal,
       fine,
       ultraFine,
       max
   };

   enum LightAttenuationType {
       none,
       linearSlow,
       linearFast,
       quadraticSlow,
       quadraticFast,
       physical
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<LightingLayer, LightingLayerProperties> properties;
   attachment<LightingLayerColorLayer, LightingLayerColorLayerProperties> properties;

   attachment<Light, LightProperties> properties;
   attachment<LightSpot, LightSpotProperties> properties;
   attachment<LightOmni, LightOmniProperties> properties;
   attachment<LightSun, LightSunProperties> properties;
   attachment<LightSky, LightSkyProperties> properties;
   attachment<LightAreaPlane, LightAreaPlaneProperties> properties;
   attachment<LightAreaCylinder, LightAreaCylinderProperties> properties;
   attachment<LightAreaMesh, LightAreaMeshProperties> properties;

   };

----

Raptor_Material.dsm
-------------------

**Domain:** Material, MaterialEnvironment, MaterialMatte, MaterialMirror, MaterialMultilayer, MaterialStandard, MaterialAxfCpa2

The **heart of the rendering system** - defines how surfaces appear. This is the largest
and most complex DSM file, showcasing concept hierarchy for material types.

Material Hierarchy
^^^^^^^^^^^^^^^^^^

Concept inheritance via ``is a``:

- ``Material`` (abstract base)
    - ``MaterialStandard`` - general-purpose PBR material (diffuse, specular, transparency)
    - ``MaterialMultilayer`` - stacked layers for complex surfaces (car paint, fabric)
    - ``MaterialMirror`` - perfect reflection with transparency
    - ``MaterialMatte`` - shadow catcher for compositing
    - ``MaterialEnvironment`` - HDR environment lighting
    - ``MaterialSeam`` - stitching/seam rendering for fabrics
    - ``MaterialAxfCpa2`` - X-Rite AxF measured material (real-world paint scans)

MaterialMultilayer Sublayers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``MaterialMultilayerLayerDiffuse`` - base color, ambient, color maps
- ``MaterialMultilayerLayerSpecular`` - highlights, roughness, fresnel
- ``MaterialMultilayerLayerIllumination`` - self-illumination, velvet effect

.. note::

   The ``is a`` relationship enables polymorphism - a ``key<Material>`` can
   reference any material type, letting surfaces accept any material without knowing its
   specific type.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Material;

   concept MaterialEnvironment is a Material;
   struct MaterialEnvironmentProperties {
       string name = "MaterialEnvironment";
       optional<key<Thumbnail>> thumbnailKey;
       float intensity = 1.0;
   };

   concept MaterialMatte is a Material;
   struct MaterialMatteProperties {
       string name = "MaterialMatte";
       optional<key<Thumbnail>> thumbnailKey;
       float threshold;
       float offset;
       float outline;
       float contrast = 1.0;
   };

   concept MaterialMirror is a Material;
   struct MaterialMirrorProperties {
       string name = "MaterialMirror";
       optional<key<Thumbnail>> thumbnailKey;
       Vector reflectionColor;
       bool isTransparent;
       Vector transparencyColor = {1.0, 1.0, 1.0};
       Vector interReflectionColor;
       MaterialMirrorOutboundSceneColor outboundSceneColor;
       bool reflectedSurfaceTagEnabled;
       string reflectedSurfaceTag;
   };

   enum MaterialMirrorOutboundSceneColor {
       black,
       background,
       environment
   };

   concept MaterialMultilayerLayer;

   enum MaterialLabelMode {
       mix,
       mul,
       add
   };

   concept MaterialMultilayer is a Material;
   struct MaterialMultilayerProperties {
       string name = "Material";
       optional<key<Thumbnail>> thumbnailKey;
       bool mipmapEnabled;
       bool layersUseRelief;
       bool isTransparent;
       vector<key<MaterialMultilayerLayer>> layerKeys;
       MaterialMultilayerRelief relief;
       TextureRepeatMode labelRepeatU;
       TextureRepeatMode labelRepeatV;
       MaterialLabelMode labelMode;
       float labelFactor = 1.0;
       bool overrideRepeatForLabel = true;
   };

   struct MaterialMultilayerBump {
       bool enabled;
       float scale = 1.0;
       optional<key<BumpMap>> mapKey;
       Transform transform;
       TextureRepeatMode mapRepeatU = .repeat;
       TextureRepeatMode mapRepeatV = .repeat;
   };

   struct MaterialMultilayerRelief {
       bool enabled;
       float scale = 1.0;
       optional<key<BumpMap>> mapKey;
       optional<key<Texture>> maximumMipmapHeightMapKey;
       optional<key<Texture>> mipmapedHeightMapKey;
       Transform reliefMapTransform;
       TextureRepeatMode mapRepeatU = .repeat;
       TextureRepeatMode mapRepeatV = .repeat;
   };

   concept MaterialMultilayerLayerIllumination is a MaterialMultilayerLayer;
   struct MaterialMultilayerLayerIlluminationProperties {
       string name = "MaterialMultilayerLayerIllumination";
       bool enabled = true;
       float intensity;
       Vector color;
       float inShadow;
       float velvetFactor;
       optional<key<Texture>> velvetMapKey;
       bool velvetMapEnabled;
       bool velvetMapModulateEnabled;
       optional<key<Texture>> modulateMapKey;
       bool modulateMapEnabled;
       TextureRepeatMode modulateMapRepeatU = .repeat;
       TextureRepeatMode modulateMapRepeatV = .repeat;
       Transform modulateMapTransform;
       bool allowTextureRepeat;
       MaterialMultilayerBump bump;
       bool useRelief;
   };

   concept MaterialMultilayerLayerDiffuse is a MaterialMultilayerLayer;
   struct MaterialMultilayerLayerDiffuseProperties {
       string name = "MaterialMultilayerLayerDiffuse";
       bool enabled = true;
       float intensity = 1.0;
       Vector color;
       Vector ambientColor;
       optional<key<Texture>> colorMapKey;
       bool colorMapEnabled = false;
       TextureRepeatMode colorMapRepeatU = .repeat;
       TextureRepeatMode colorMapRepeatV = .repeat;
       Transform colorMapTransform;
       float alphaModulator = 1.0;
       optional<key<Texture>> alphaMapKey;
       TextureRepeatMode alphaMapRepeatU = .repeat;
       TextureRepeatMode alphaMapRepeatV = .repeat;
       Transform alphaMapTransform;
       optional<key<Texture>> filterMapKey;
       bool filterMapEnabled;
       MaterialMultilayerBump bump;
       bool useRelief;
   };

   concept MaterialMultilayerLayerSpecular is a MaterialMultilayerLayer;
   struct MaterialMultilayerLayerSpecularProperties {
       string name = "MaterialMultilayerLayerSpecular";
       bool enabled = true;
       float roughness;
       float intensity = 1.0;
       float inShadow;
       bool fresnelEnabled = false;
       float fresnelRefraction;
       float fresnelExtinction;
       bool transmissionAttenuationEnabled;
       optional<key<Texture>> modulateMapKey;
       bool modulateMapEnabled;
       TextureRepeatMode modulateMapRepeatU = .repeat;
       TextureRepeatMode modulateMapRepeatV = .repeat;
       Transform modulateMapTransform;
       optional<key<Texture>> roughnessMapKey;
       bool roughnessMapEnabled;
       TextureRepeatMode roughnessMapRepeatU = .repeat;
       TextureRepeatMode roughnessMapRepeatV = .repeat;
       Transform roughnessMapTransform;
       Vector filter;
       Vector diffuseFilter;
       optional<key<Texture>> filterMapKey;
       bool filterMapEnabled;
       MaterialMultilayerBump bump;
       bool useRelief;
   };

   concept MaterialSeam is a Material;
   struct MaterialSeamProperties {
       string name = "MaterialSeam";
       optional<key<Thumbnail>> thumbnailKey;
       Vector diffuseColor;
       Vector ambientColor;
       float diffuseIntensity = 1.0;
       optional<key<Texture>> diffuseMapKey;
       bool diffuseMapEnabled;
       optional<key<Texture>> seamMapKey;
       bool seamMapEnabled;
       optional<key<BumpMap>> seamBumpMapKey;
       float specularRoughness;
       float specularIntensity;
       Vector specularFilter;
       Vector specularDiffuseFilter;
       optional<key<BumpMap>> pleatMapKey;
       bool pleatMapEnabled;
       float pleatMapBumpScale;
       bool keepAspectRatio;
       bool mipmapEnabled;
       Transform transformation;
       bool bumpDiffuseEnabled;
       float bumpDiffuseScale;
       bool bumpSpecularEnabled;
       float bumpSpecularScale;
   };

   concept MaterialStandard is a Material;

   enum MaterialStandardType {
       diffuse,
       diffuseSpecular,
       transparent
   };

   struct MaterialStandardProperties {
       string name = "MaterialStandard";
       optional<key<Thumbnail>> thumbnailKey;
       MaterialStandardType materialType = .diffuseSpecular;
       Vector diffuseColor;
       Vector ambientColor;
       Vector illuminationColor;
       float diffuseIntensity;
       float illuminationIntensity;
       optional<key<Texture>> diffuseMapKey;
       bool diffuseMapEnabled;
       TextureRepeatMode diffuseMapRepeatU = .repeat;
       TextureRepeatMode diffuseMapRepeatV = .repeat;
       Transform diffuseMapTransform;
       float alphaModulator;
       optional<key<Texture>> alphaMapKey;
       Transform alphaMapTransform;
       TextureRepeatMode alphaMapRepeatU = .repeat;
       TextureRepeatMode alphaMapRepeatV = .repeat;
       optional<key<Texture>> diffuseFilterMapKey;
       bool diffuseFilterMapEnabled;
       optional<key<BumpMap>> bumpMapKey;
       Transform bumpMapTransform;
       TextureRepeatMode bumpMapRepeatU = .repeat;
       TextureRepeatMode bumpMapRepeatV = .repeat;
       bool bumpDiffuseEnabled;
       float bumpDiffuseScale;
       bool bumpSpecularEnabled;
       float bumpSpecularScale;
       optional<key<Texture>> maximumMipmapHeightMapKey;
       optional<key<Texture>> mipmapedHeightMapKey;
       bool reliefBumpEnabled;
       float reliefBumpScale;
       float specularRoughness;
       float specularIntensity;
       float specularInShadow;
       bool fresnelEnabled;
       float fresnelRefraction;
       float fresnelExtinction;
       bool diffuseAttenuationEnabled;
       bool velvetEnabled;
       float velvetFactor;
       optional<key<Texture>> velvetMapKey;
       bool velvetMapEnabled;
       bool velvetMapModulateEnabled;
       optional<key<Texture>> specularModulateMapKey;
       bool specularModulateMapEnabled;
       TextureRepeatMode specularModulateMapRepeatU = .repeat;
       TextureRepeatMode specularModulateMapRepeatV = .repeat;
       Transform specularModulateMapTransform;
       optional<key<Texture>> roughnessMapKey;
       bool roughnessMapEnabled;
       TextureRepeatMode roughnessMapRepeatU = .repeat;
       TextureRepeatMode roughnessMapRepeatV = .repeat;
       Transform roughnessMapTransform;
       bool roughnessMapIsGloss;
       Vector specularFilter;
       Vector specularDiffuseFilter;
       bool transformationLink;
       bool mipmapEnabled;
       TextureRepeatMode labelRepeatU;
       TextureRepeatMode labelRepeatV;
       MaterialLabelMode labelMode;
       float labelFactor = 1.0;
   };

   concept MaterialAxfCpa2 is a Material;
   struct MaterialAxfCpa2Properties {
       string name = "MaterialAxfCpa2";
       optional<key<Thumbnail>> thumbnailKey;
       float diffuse = 1.0;
       vector<float> coeffs;
       vector<float> f0s;
       vector<float> spreads;
       float ior = 1.0;
       bool refraction = true;
       optional<key<BumpMap>> clearCoatBumpMapKey;
       int32 numThetaF;
       int32 numThetaI;
       int32 maxThetaI;
       vector<int32> sliceLUT;
       Transform clearCoatTransform;
       Transform flakesTransform;
       optional<key<Texture>> colorsKey;
       optional<key<TextureArray>> flakesKey;
       float hueShift;
       float saturation = 1.0;
       float contrast = 1.0;
       float exposure = 1.0;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<MaterialEnvironment, MaterialEnvironmentProperties> properties;
   attachment<MaterialMatte, MaterialMatteProperties> properties;
   attachment<MaterialMirror, MaterialMirrorProperties> properties;
   attachment<MaterialMultilayer, MaterialMultilayerProperties> properties;
   attachment<MaterialMultilayerLayerIllumination, MaterialMultilayerLayerIlluminationProperties> properties;
   attachment<MaterialMultilayerLayerDiffuse, MaterialMultilayerLayerDiffuseProperties> properties;
   attachment<MaterialMultilayerLayerSpecular, MaterialMultilayerLayerSpecularProperties> properties;
   attachment<MaterialSeam, MaterialSeamProperties> properties;
   attachment<MaterialStandard, MaterialStandardProperties> properties;
   attachment<MaterialAxfCpa2, MaterialAxfCpa2Properties> properties;

   };

----

Raptor_Math.dsm
---------------

**Domain:** Core mathematical types

Foundational structs used throughout the Raptor model.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   struct Vector {
       float x;
       float y;
       float z;
   };

   struct Aabb {
       Vector min;
       Vector max;
   };

   struct Transform {
       Vector translation;
       Vector orientation;
       Vector scaling = {1.0, 1.0, 1.0};
   };

   struct Plane {
       Vector normal;
       float q;
   };

   struct PointOfView {
       Vector target;
       Vector eye = {2.0, 2.0, 2.0};
       Vector up = {0.0, 1.0, 0.0};
   };

   };

----

Raptor_Mesh.dsm
---------------

**Domain:** Mesh, MeshAnimation, Thumbnail

Defines 3D geometry data with support for animation and preview thumbnails.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Mesh;
   struct MeshProperties {
       Aabb aabb;
       int32 triangleCount;
       int32 vertexCount;
       blob_id blob_indices;
       blob_id blob_positions;
       blob_id blob_normals;
       blob_id blob_tangents;
       blob_id blob_binormals;
       blob_id blob_lightmapUvs;
       map<int8, blob_id> blob_uvs;
       map<key<LightingLayer>, blob_id> blob_directions;
       blob_id blob_animation;
   };

   concept MeshAnimation;
   struct MeshAnimationProperties {
       int32 vertexCount;
       int32 defaultFrame;
       vector<MeshAnimationFrame> frames;
   };

   struct MeshAnimationFrame {
       Aabb aabb;
       blob_id blob_positions;
       blob_id blob_normals;
       blob_id blob_tangents;
       blob_id blob_binormals;
   };

   concept Thumbnail;
   struct ThumbnailProperties {
       string name = "Thumbnail";
       vector<Mipmap> mipmaps;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Mesh, MeshProperties> properties;
   attachment<MeshAnimation, MeshAnimationProperties> properties;
   attachment<Thumbnail, ThumbnailProperties> properties;

   };

----

Raptor_Model.dsm
----------------

**Domain:** Model, GeometryLayer, PositionLayer

Defines the **scene graph structure** - how 3D geometry is organized hierarchically.

Concepts
^^^^^^^^

- ``Model``: root container for a complete 3D model (e.g., a car)
- ``GeometryLayer``: hierarchical node containing Surfaces and child GeometryLayers (tree
  structure)
- ``PositionLayer``: transformation overrides for kinematics (different
  poses/configurations)

Key Relationships
^^^^^^^^^^^^^^^^^

- Model references LightingLayers, Kinematics, PositionLayers, BezierPaths
- GeometryLayer uses tree structure via ``childrenKeys``, contains ``surfaceKeys``
- PositionLayer stores ``localToPivot`` and ``pivotToParent`` transforms per
  KinematicsElement

This hierarchical model enables part visibility toggling, level-of-detail, and
configuration variants (e.g., car with/without spoiler).

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Model;
   struct ModelProperties {
       string name = "Model";
       vector<key<LightingLayer>> lightingLayerKeys;
       key<GeometryLayer> rootGeometryLayerKey;
       key<Kinematics> kinematicsKey;
       vector<key<PositionLayer>> positionLayerKeys;
       vector<key<BezierPath>> bezierPathKeys;
   };

   concept GeometryLayer;
   struct GeometryLayerProperties {
       string name = "GeometryLayer";
       bool enabled = true;
       vector<key<GeometryLayer>> childrenKeys;
       vector<key<Surface>> surfaceKeys;
   };

   concept PositionLayer;
   struct PositionLayerProperties {
       string name = "PositionLayer";
       bool enabled;
       map<key<KinematicsElement>, Transform> localToPivot;
       map<key<KinematicsElement>, Transform> pivotToParent;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Model, ModelProperties> properties;
   attachment<GeometryLayer, GeometryLayerProperties> properties;
   attachment<PositionLayer, PositionLayerProperties> properties;

   };

----

Raptor_Product.dsm
------------------

**Domain:** Product, AspectLayer

Defines products with material variants (AspectLayers) and configuration options.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Product;
   struct ProductProperties {
       string name = "Product";
       optional<key<Thumbnail>> thumbnailKey;
       key<Model> modelKey;
       vector<key<AspectLayer>> aspectLayerKeys;
       bool materialsHideLabelsBelow;
       map<key<Surface>, SurfaceRenderProperties> surfaceRenderProperties;
       vector<key<EnvironmentLayer>> environmentLayerKeys;
       map<key<Environment>, EnvironmentRenderProperties> environmentRenderProperties;
       map<string, set<string>> configurationBookmarks;
       set<string> configurationDefines;
       bool ignoreBackfaceCull;
       bool environmentLinkedToDiffuse = true;
       SunAuthoringProperties sunAuthoring;
       SSAOProperties ssao;
   };

   enum BackfaceCullMode {
       show,
       default,
       hide
   };

   struct SurfaceRenderProperties {
       bool isHidden;
       BackfaceCullMode backfaceCullMode = .default;
       bool transparencyDepthWrite;
   };

   struct MaterialAssignment {
       key<Material> materialKey;
       Transform transform;
       int8 uvSet;
       Plane mirrorPlane;
   };

   struct LabelAssignment {
       string name = "LabelAssignment";
       bool enabled = true;
       MaterialAssignment materialAssignment;
   };

   concept AspectLayer;
   struct AspectLayerProperties {
       string name = "AspectLayer";
       bool enabled;
       map<key<Surface>, MaterialAssignment> materialAssignments;
       map<key<Surface>, vector<LabelAssignment>> labelAssignments;
   };

   struct SSAOProperties {
       bool enabled;
       bool lightmaps = true;
       bool transparentSurfaces;
       float radius = 0.05;
       float intensity = 1.0;
       float bias = 8.0;
       uint16 steps = 4;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Product, ProductProperties> properties;
   attachment<AspectLayer, AspectLayerProperties> properties;

   };

----

Raptor_Sensor.dsm
-----------------

**Domain:** Sensor, Background, Overlay, OverlayLayer, PostProcess

Defines render output settings including backgrounds, overlays, and post-processing effects.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Sensor;

   enum SensorBackgroundType {
       none,
       gradient,
       environment
   };

   struct SensorProperties {
       string name = "Sensor";
       optional<key<Thumbnail>> thumbnailKey;
       bool isometric;
       bool dynamicAspectRatio;
       float width = 0.024;
       float height = 0.036;
       optional<key<Background>> backgroundKey;
       SensorBackgroundType backgroundType;
       optional<key<Overlay>> overlayKey;
       bool overlayVisibility;
       optional<key<PostProcess>> postprocessKey;
       bool postprocessVisibility;
   };

   concept Background;
   struct BackgroundProperties {
       string name = "Background";
       optional<key<Thumbnail>> thumbnailKey;
       Vector gradientStart = {0.455, 0.455, 0.455};
       Vector gradientEnd = {0.455, 0.455, 0.455};
       bool gradientActivated = true;
       float gradientOrientationAngle;
       bool preserveTextureAspect = true;
       optional<key<Texture>> textureKey;
       bool textureEnabled;
       Transform textureTransform;
   };

   concept Overlay;
   struct OverlayProperties {
       string name = "Overlay";
       optional<key<Thumbnail>> thumbnailKey;
       float alpha = 1.0;
       vector<key<OverlayLayer>> layerKeys;
   };

   concept OverlayLayer;
   struct OverlayLayerProperties {
       string name = "OverlayLayer";
       bool enabled;
       OverlayLayerType layerType = .sprite;
       OverlayLayerSizeType layerSize;
       float width = 0.25;
       float height = 0.25;
       OverlayLayerLengthUnit widthUnit;
       OverlayLayerLengthUnit heightUnit;
       bool constrainedRotation = true;
       OverlayLayerVerticalAlignment verticalAlignment = .bottom;
       OverlayLayerHorizontalAlignment horizontalAlignment;
       Transform transform;
       OverlayLayerLengthUnit offsetUUnit;
       OverlayLayerLengthUnit offsetVUnit;
       Vector gradientColorStart = {1.0, 1.0, 1.0};
       Vector gradientColorEnd = {1.0, 1.0, 1.0};
       float gradientAlphaStart = 1.0;
       float gradientAlphaEnd = 1.0;
       bool gradientFlipVertically;
       bool gradientFlipHorizontally;
       optional<key<Texture>> textureKey;
       bool textureEnabled;
       Transform textureTransform;
   };

   enum OverlayLayerHorizontalAlignment {
       left,
       middle,
       right
   };

   enum OverlayLayerLengthUnit {
       pixel,
       millimeters,
       centimeters,
       inches,
       relativeToX,
       relativeToY
   };

   enum OverlayLayerSizeType {
       texture,
       screen,
       userDefined
   };

   enum OverlayLayerType {
       sticker,
       sprite
   };

   enum OverlayLayerVerticalAlignment {
       top,
       middle,
       bottom
   };

   concept PostProcess;
   struct PostProcessProperties {
       string name = "PostProcess";
       optional<key<Thumbnail>> thumbnailKey;
       bool applyToBackground = true;
       bool applyToOverlay = true;
       optional<uint32> soloEffectIndex;
       vector<PostProcessEffect> effects;
   };

   enum PostProcessDataType {
       bool,
       int,
       float,
       color,
       length,
       texture,
       levels,
       cameraResponseEnum
   };

   struct PostProcessEffect {
       string name = "PostProcessEffect";
       PostProcessEffectType effectType;
       bool enabled;
       vector<PostProcessEffectParameter> parameters;
   };

   struct PostProcessEffectParameter {
       string name = "PostProcessEffectParameter";
       int32 parameterLength = 1;
       PostProcessLengthUnit lengthUnit = .none;
       PostProcessDataType dataType = .float;
       string parameterValue = "0/";
   };

   enum PostProcessEffectType {
       negative,
       blackAndWhite,
       sepia,
       grayscale,
       colorFilter,
       blurHorizontal,
       blurVertical,
       grainGeneratorPerlin,
       grainGeneratorMd4,
       edgeDetector,
       combine,
       erodeHorizontal,
       erodeVertical,
       erode,
       dilateHorizontal,
       dilateVertical,
       dilate,
       adjustColor,
       automaticToneMapping,
       blur,
       grain,
       handDrawing,
       store,
       restore,
       get3DImage,
       glowThresholder,
       glowCombiner,
       glow,
       sharpenCombiner,
       sharpen,
       multiplyAdd,
       bloom,
       levels,
       bloomCombiner,
       reinhardToneMapping,
       dragoToneMapping,
       bloomThresholder,
       vignetting,
       cameraResponse
   };

   enum PostProcessLengthUnit {
       pixel,
       millimeter,
       none,
       relativeToX,
       relativeToY,
       relativeToDefault
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Sensor, SensorProperties> properties;
   attachment<Background, BackgroundProperties> properties;
   attachment<Overlay, OverlayProperties> properties;
   attachment<OverlayLayer, OverlayLayerProperties> properties;
   attachment<PostProcess, PostProcessProperties> properties;

   };

----

Raptor_Surface.dsm
------------------

**Domain:** Surface

Defines 3D surfaces (geometry instances) with mesh references and rendering properties.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Surface;
   struct SurfaceProperties {
       string name = "Surface";
       map<key<LightingLayer>, key<Texture>> lightmaps;
       key<Mesh> meshKey;
       Vector color = {1.0, 1.0, 1.0};
       set<string> tags;
       SurfaceBillboardMode billboardMode;
       optional<key<MeshAnimation>> meshAnimationKey;
       SurfaceMirrorPlane mirrorPlane;
   };

   enum SurfaceBillboardMode {
       none,
       rotateY,
       rotateXy
   };

   struct SurfaceMirrorPlane {
       Vector position;
       Vector normal = {0.0, 1.0, 0.0};
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Surface, SurfaceProperties> properties;

   };

----

Raptor_Texture.dsm
------------------

**Domain:** BumpMap, Texture, TextureCube, TextureArray, Video

Defines **texture assets** used by materials for color, bump, and environment mapping.

Texture Types
^^^^^^^^^^^^^

- ``Texture``: 2D image with mipmaps (diffuse, specular, alpha maps)
- ``TextureCube``: 6-face cubemap for environment reflections (xPos, xNeg, yPos, yNeg, zPos, zNeg)
- ``TextureArray``: stack of textures for layered effects (car paint flakes)
- ``BumpMap``: normal/height maps for surface detail
- ``Video``: animated texture source

Key Structures
^^^^^^^^^^^^^^

- ``Mipmap``: single mip level with ``width``, ``height``, ``format``, and ``blob_id`` referencing pixel data
- ``TextureRepeatMode``: enum for UV wrapping (repeat, clamp, mirror)

.. note::

   **Blob pattern**: Actual pixel data is stored in ``blob_id`` references, not inline -
   enabling efficient deduplication and streaming of large textures.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   struct Mipmap {
       int32 width;
       int32 height;
       blob_id blob_image;
   };

   concept BumpMap;
   struct BumpMapProperties {
       string name = "BumpMap";
       optional<key<Thumbnail>> thumbnailKey;
       vector<Mipmap> mipmaps;
   };

   concept Texture;
   struct TextureProperties {
       string name = "Texture";
       optional<key<Thumbnail>> thumbnailKey;
       vector<Mipmap> mipmaps;
       optional<key<Video>> videoKey;
   };

   concept TextureCube;
   struct TextureCubeProperties {
       string name = "TextureCube";
       vector<Mipmap> xPosMipmaps;
       vector<Mipmap> xNegMipmaps;
       vector<Mipmap> yPosMipmaps;
       vector<Mipmap> yNegMipmaps;
       vector<Mipmap> zPosMipmaps;
       vector<Mipmap> zNegMipmaps;
   };

   concept TextureArray;
   struct TextureArrayProperties {
       string name = "TextureArray";
       optional<key<Thumbnail>> thumbnailKey;
       vector<vector<Mipmap>> textures;
   };

   enum TextureRepeatMode {
       clamp,
       repeat,
       mirroredRepeat
   };

   concept Video;
   struct VideoProperties {
       string name = "Video";
       optional<key<Thumbnail>> thumbnailKey;
       float duration;
       blob_id blob_video;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<BumpMap, BumpMapProperties> properties;
   attachment<Texture, TextureProperties> properties;
   attachment<TextureCube, TextureCubeProperties> properties;
   attachment<TextureArray, TextureArrayProperties> properties;
   attachment<Video, VideoProperties> properties;

   };

----

Raptor_Timeline.dsm
-------------------

**Domain:** Timeline, TimelineClip, TimelineClipCameraBezierPath, TimelineClipCameraBookmark

Defines the **animation system** for creating cinematic sequences. Timelines contain clips
that animate cameras, configurations, and properties over time.

Timeline Structure
^^^^^^^^^^^^^^^^^^

- ``Timeline``: container with tracks (TimelineTrack) and triggers
- ``TimelineTrack``: ordered sequence of clips on a single channel
- ``TimelineClip``: base concept for all animation clips

Clip Types
^^^^^^^^^^

TimelineClip hierarchy:

- ``TimelineClipCameraBezierPath``: animate camera along a Bezier spline
- ``TimelineClipCameraBookmark``: jump between saved camera positions
- ``TimelineClipCameraKamFile``: import external camera animation
- ``TimelineClipConfiguration``: switch product configurations over time
- ``TimelineClipVideo``: play video textures
- ``TimelineClipChannelCurve``: animate any property with keyframes and curves
- ``TimelineClipChannelBaked``: pre-computed animation data
- ``TimelineClipChannelSimple``: linear interpolation between two values

Triggers
^^^^^^^^

- ``TimelineTriggerKey``: trigger actions at specific frames (keyboard shortcuts)
- ``TimelineTriggerSurface``: trigger when clicking surfaces (interactive presentations)

This enables creating product configurators, turntable animations, and interactive
experiences.

.. code-block:: dsm

   // Types
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   concept Timeline;
   struct TimelineProperties {
       string name = "Timeline";
       float timeStart;
       float timeEnd;
       vector<TimelineTrack> tracks;
   };

   club TimelineAnimation;
   membership TimelineAnimation Timeline;
   membership TimelineAnimation TimelineClipCameraBezierPath;
   membership TimelineAnimation TimelineClipCameraBookmark;
   membership TimelineAnimation TimelineClipCameraKamFile;
   membership TimelineAnimation TimelineClipChannelBaked;
   membership TimelineAnimation TimelineClipChannelCurve;
   membership TimelineAnimation TimelineClipChannelSimple;
   membership TimelineAnimation TimelineClipConfiguration;
   membership TimelineAnimation TimelineClipProduct;
   membership TimelineAnimation TimelineClipVideo;

   concept TimelineClip;

   concept TimelineClipCameraBezierPath is a TimelineClip;
   struct TimelineClipCameraBezierPathProperties {
       string name = "TimelineClipCameraBezierPath";
       float duration;
       TimelineClipCameraBezierPathPosition positionType = .fixed;
       TimelineClipCameraBezierPathDirection directionType = .fixedDirection;
       optional<key<BezierPath>> bezierPathUsedForPositionKey;
       optional<key<BezierPath>> bezierPathUsedForDirectionKey;
       bool invertBezierPathUsedForPosition;
       bool invertBezierPathUsedForDirection;
       optional<key<KinematicsNodeNull>> nullUsedForPositionKey;
       optional<key<KinematicsNodeNull>> nullUsedForDirectionKey;
       Vector fixedPositionFrom = {1.0, 1.0, 1.0};
       Vector fixedPositionTo;
       Vector fixedDirection = {0.0, 0.0, 1.0};
       Vector fixedDirectionUp = {0.0, 1.0, 0.0};
       Vector fixedTargetPosition;
   };

   enum TimelineClipCameraBezierPathDirection {
       followBezierPath,
       followBezierPathPosition,
       fixedDirection,
       fixedPosition,
       followNull
   };

   enum TimelineClipCameraBezierPathPosition {
       followBezierPath,
       fixed,
       followNull
   };

   concept TimelineClipCameraBookmark is a TimelineClip;
   struct TimelineClipCameraBookmarkProperties {
       string name = "TimelineClip";
       float duration;
       float fps;
       float sleepAddCst;
       float sleepMulCst;
       float durationAddCst;
       float durationMulCst;
       bool closedPath;
       vector<TimelineClipCameraBookmarkBookmark> bookmarks;
   };

   struct TimelineClipCameraBookmarkBookmark {
       string name = "Bookmark";
       bool enabled;
       TimelineClipCameraProperties cameraProperties;
       TimelineClipCameraBookmarkTransition transition = .linear;
       float transitionSleep;
       float transitionSmoothness;
       float transitionDuration = 1.0;
       float transitionTurn = 1.0;
       float transitionTurnDuration = 1.0;
   };

   enum TimelineClipCameraBookmarkTransition {
       linear,
       jump,
       orbit,
       head,
       spline
   };

   struct TimelineClipCameraFieldOfView {
       CameraFovType fovType;
       float fov = 0.7853981634;
   };

   concept TimelineClipCameraKamFile is a TimelineClip;
   struct TimelineClipCameraKamFileProperties {
       string name = "TimelineClip";
       float duration;
       key<TimelineKamFile> kamFileKey;
   };

   struct TimelineClipCameraProperties {
       TimelineClipCameraFieldOfView fieldOfView;
       PointOfView pointOfView;
   };

   concept TimelineClipChannelBaked is a TimelineClip;
   struct TimelineClipChannelBakedProperties {
       string name = "TimelineClip";
       float duration;
       blob_id blob_transforms;
       uuid target;
       uuid subTarget;
       uuid elementType;
       uuid element;
   };

   concept TimelineClipChannelCurve is a TimelineClip;
   struct TimelineClipChannelCurveProperties {
       string name = "TimelineClip";
       float duration;
       vector<TimelineClipChannelCurveChannel> channels;
   };

   struct TimelineClipChannelCurveChannel {
       Vector color;
       vector<TimelineClipChannelCurveKeyframe> keyframes;
       uuid target;
       uuid subTarget;
       uuid elementType;
       uuid element;
   };

   struct TimelineClipChannelCurveKeyframe {
       float time;
       float value;
       Vector leftTangent;
       Vector rightTangent;
       TimelineClipChannelCurveTangent rightTangentType = .linear;
   };

   enum TimelineClipChannelCurveTangent {
       bezier,
       linear,
       step
   };

   concept TimelineClipChannelSimple is a TimelineClip;
   struct TimelineClipChannelSimpleProperties {
       string name = "TimelineClip";
       float duration;
       float valueStart;
       float valueEnd;
       TimelineClipChannelSimpleEasing easing = .linear;
       uuid target;
       uuid subTarget;
       uuid elementType;
       uuid element;
   };

   enum TimelineClipChannelSimpleEasing {
       linear,
       inQuad,
       outQuad,
       inOutQuad
   };

   concept TimelineClipConfiguration is a TimelineClip;
   struct TimelineClipConfigurationProperties {
       string name = "TimelineClip";
       vector<TimelineClipConfigurationParameter> parameters;
   };

   struct TimelineClipConfigurationParameter {
       string name = "TimelineClipConfigurationParameter";
       string value;
       bool isBinary;
   };

   concept TimelineClipProduct is a TimelineClip;
   struct TimelineClipProductProperties {
       string name = "TimelineClip";
       key<Product> productKey;
   };

   concept TimelineClipVideo is a TimelineClip;
   struct TimelineClipVideoProperties {
       string name = "TimelineClip";
       float duration;
       key<Video> videoKey;
   };

   concept TimelineData;
   struct TimelineDataProperties {
       vector<key<Timeline>> timelineKeys;
       vector<key<TimelineClip>> clipKeys;
       vector<key<TimelineTrigger>> triggerKeys;
   };

   concept TimelineKamFile;
   struct TimelineKamFileProperties {
       float fps = 30.0;
       bool ignoreFov;
       bool swapFov;
       blob_id blob_frames;
   };

   enum TimelineLoopType {
       none,
       repeated,
       incremented
   };

   enum TimelineTrackType {
       product,
       configuration,
       camera,
       channels,
       video
   };

   struct TimelineTrack {
       TimelineTrackType trackType = .channels;
       vector<TimelineTrackEntry> entries;
   };

   struct TimelineTrackEntry {
       key<TimelineClip> clipKey;
       bool isReversed;
       TimelineLoopType loopType;
       float time;
   };

   concept TimelineTrigger;

   struct TimelineTriggerAnimation {
       TimelineTriggerPlayMode playMode;
       key<TimelineAnimation> animationKey;
   };

   concept TimelineTriggerKey is a TimelineTrigger;
   struct TimelineTriggerKeyProperties {
       int64 key;
       vector<TimelineTriggerAnimation> animations;
   };

   enum TimelineTriggerPlayMode {
       continued,
       reset,
       invertWithPause,
       invertWithoutPause
   };

   concept TimelineTriggerSurface is a TimelineTrigger;
   struct TimelineTriggerSurfaceProperties {
       key<Surface> surfaceKey;
       vector<TimelineTriggerAnimation> animations;
   };

   };

   // Attachments
   namespace Raptor {f2d9ea90-2adc-4e9a-a2bf-02288281747d} {

   attachment<Timeline, TimelineProperties> properties;
   attachment<TimelineClipCameraBezierPath, TimelineClipCameraBezierPathProperties> properties;
   attachment<TimelineClipCameraBookmark, TimelineClipCameraBookmarkProperties> properties;
   attachment<TimelineClipCameraKamFile, TimelineClipCameraKamFileProperties> properties;
   attachment<TimelineClipChannelBaked, TimelineClipChannelBakedProperties> properties;
   attachment<TimelineClipChannelCurve, TimelineClipChannelCurveProperties> properties;
   attachment<TimelineClipChannelSimple, TimelineClipChannelSimpleProperties> properties;
   attachment<TimelineClipConfiguration, TimelineClipConfigurationProperties> properties;
   attachment<TimelineClipProduct, TimelineClipProductProperties> properties;
   attachment<TimelineClipVideo, TimelineClipVideoProperties> properties;
   attachment<TimelineData, TimelineDataProperties> properties;
   attachment<TimelineKamFile, TimelineKamFileProperties> properties;
   attachment<TimelineTriggerKey, TimelineTriggerKeyProperties> properties;
   attachment<TimelineTriggerSurface, TimelineTriggerSurfaceProperties> properties;

   };
