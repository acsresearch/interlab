cd `dirname $0`

npm run build

TARGET_PATH=../interlab/ui/browser

rm -rf ${TARGET_PATH:?}/*
cp -r build/* ${TARGET_PATH}
git add ${TARGET_PATH}
