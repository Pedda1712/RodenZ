rm -rf ${BUILDPREFIX}venv_build
rm -rf ${BUILDPREFIX}build
python3 -m venv ${BUILDPREFIX}venv_build
source ${BUILDPREFIX}venv_build/bin/activate
pip install build
python -m build ${BUILDPREFIX}Libraries/RZVisuals --outdir build
python -m build ${BUILDPREFIX}Tools/RZCameraExtrinsicsTool --outdir build
python -m build ${BUILDPREFIX}Libraries/RZTrainingPipeline --outdir build
python -m build ${BUILDPREFIX}Tools/RZTrainDLC --outdir build
python -m build ${BUILDPREFIX}Tools/RZCameraCalibration --outdir build
python -m build ${BUILDPREFIX}Tools/RZTriangulation --outdir build
python -m build ${BUILDPREFIX}Tools/RZBayesianReconstruction --outdir build
python -m build ${BUILDPREFIX}Tools/RZCorrect2D --outdir build
python -m build ${BUILDPREFIX}Tools/RZView2DCSV --outdir build
python -m build ${BUILDPREFIX}Tools/RZView3DCSV --outdir build
python -m build ${BUILDPREFIX}Tools/RZEvaluate --outdir build
rm -rf ${BUILDPREFIX}venv_build
