mkdir ProductDownload
cd ProductDownload


wget https://github.com/kraftek/awsdownload/releases/download/1.7/ProductDownload-1.7.zip
unzip ProductDownload-1.7.zip
rm ProductDownload-1.7.zip

#wget https://github.com/kraftek/awsdownload/releases/download/1.5.1/ProductDownload-1.5.1.zip
#unzip ProductDownload-1.5.1.zip
#rm ProductDownload-1.5.1.zip

# sen2cor
wget http://step.esa.int/thirdparties/sen2cor/2.4.0/Sen2Cor-2.4.0-Linux64.run
bash Sen2Cor-2.4.0-Linux64.run
rm Sen2Cor-2.4.0-Linux64.run
