# Pipeline for chessboard recosntruction

# Check the integrity of the videos
# Extract frames from the videos
# Remove 1 frame every other one (Resource problems, RAM)
# Execute openMVG to obtain intrinsics and poses
# Generate the features files
# Generate the new descriptors files
# Generate the pairs file and the matching one
# Execute the reconstruction from known posespip show numpy matplotlib

# Paths
if ! command -v yq &>/dev/null; then
  echo "Error: 'yq' command not found. Please install yq"
  echo "Linux example: sudo apt-get install yq"
  echo "macOS example: brew install yq"
  exit 1
fi

config_file="../config_file.yml"
MAIN=$(yq e '.working_path' "$config_file")

./utils_bash/repair.sh && \
./utils_bash/extract_frames.sh && \
for SCENE in "$MAIN"/*/; do
  scene_name=$(basename ${SCENE})
  yq eval --inplace ".scene = \"$scene_name\"" $config_file
  ./utils_bash/select_frames.sh && \
  ./openMVG/ZED2.sh && \
  python3 OpenCV/corners_feat_file.py && \
  ./openMVG/copy_desc.sh && \
  python3 OpenCV/matches.py && \
  ./openMVG/ZED2_KnownPoses.sh && \
  pyhton3 Error_study/plane3D.py && \
  pyhton3 Error_study/scale.py && \
  pyhton3 Error_study/rescale.py && \
  pyhton3 Error_study/measures.py && \
  pyhton3 Error_study/reprojection.py && \
  pyhton3 Error_study/depth.py
done