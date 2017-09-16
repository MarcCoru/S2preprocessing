mkdir ProductDownload
cd ProductDownload

wget https://github.com/kraftek/awsdownload/releases/download/1.7/ProductDownload-1.7.zip
unzip ProductDownload-1.7.zip
rm ProductDownload-1.7.zip
cd ..

#wget https://github.com/kraftek/awsdownload/releases/download/1.5.1/ProductDownload-1.5.1.zip
#unzip ProductDownload-1.5.1.zip
#rm ProductDownload-1.5.1.zip

# sen2cor
wget http://step.esa.int/thirdparties/sen2cor/2.4.0/Sen2Cor-2.4.0-Linux64.run
bash Sen2Cor-2.4.0-Linux64.run
rm Sen2Cor-2.4.0-Linux64.run

# create anaconda environment with latest GDAL 2.2.1
conda create -y -c conda-forge bkreider --prefix ./conda python=2.7 pip gdal postgis

# pip packages
source activate conda

pip install psycopg2
pip install pandas
pip install shapely
pip install numpy

source deactivate

if [[ $EUID -ne 0 ]]; then
   echo "Skipping installation of postgis (required for upload.sh), no root permissions"
   exit 1
fi
# database tools (raster2pgsql)
sudo apt-get install postgis -y
