	# Documentation below describes the Linux commands needed to set up a fresh dev environvment.
	# Similar commands can be used with Homebrew on OSX to set up a OSX dev environment.
	# Below commands can also be used with Docker to make a Dockerfile with all dependencies to run
	# the pipeline. 
	
	# Dev tools
	sudo apt-get install vim
	sudo apt-get install git
	sudo apt-get install python-pip
	sudo apt-get install r-base
	sudo apt-get install python-tk
	
	# Get pipeline code and install Python dependencies
	cd ~/Desktop
	mkdir pipeline
	cd pipeline
	git clone https://github.com/markoglasgow/python_pipeline.git .
	pip install -r requirements.txt

	# Install R and R Studio
    cd ~/Desktop
	wget https://download1.rstudio.org/rstudio-xenial-1.1.383-amd64.deb
	sudo apt install ./rstudio-xenial-1.1.383-amd64.deb

	# Configure R dependencies
	sudo apt-get install openssl libssl-dev libssh2-1-dev libcurl4-openssl-dev
	touch ~/.Rprofile
	echo "options(repos=structure(c(CRAN=\"http://cran.uk.r-project.org\")))" > ~/.Rprofile

	# Install devtools then use them to install CCube
	Rscript -e 'install.packages("devtools", dependencies = TRUE)'
	Rscript -e 'devtools::install_github("keyuan/ccube")'
	Rscript -e 'install.packages("foreach", dependencies = TRUE)'

	# Install pypy to use with PyClone and PhyloWGS. 
	sudo apt-get install python-dev libopenblas-dev liblapack-dev cython
	cd ~/Desktop
	mkdir pypy
	cd pypy
	
	wget https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.9-linux_x86_64-portable.tar.bz2
	tar xvf pypy-5.9-linux_x86_64-portable.tar.bz2
	pypy-5.9-linux_x86_64-portable/bin/pypy -m ensurepip
	pypy-5.9-linux_x86_64-portable/bin/pip2.7 install -U pip wheel
	pypy-5.9-linux_x86_64-portable/bin/pip2.7 install PyYAML numpy pandas
	pypy-5.9-linux_x86_64-portable/bin/pip2.7 install scipy
	pypy-5.9-linux_x86_64-portable/bin/pip2.7 install ete2 PyVCF
	sudo mv pypy-5.9-linux_x86_64-portable /opt
	sudo ln -s /opt/pypy-5.9-linux_x86_64-portable/bin/pypy /usr/bin/pypy
	rm pypy-5.9-linux_x86_64-portable.tar.bz2
	
	wget https://bitbucket.org/aroth85/pydp/downloads/PyDP-0.2.2.tar.gz
	tar xvf PyDP-0.2.2.tar.gz
	cd PyDP-0.2.2
	pypy setup.py install
	cd ..
	rm -rf PyDP-0.2.2
	rm PyDP-0.2.2.tar.gz
	
	wget https://bitbucket.org/aroth85/pyclone/downloads/PyClone-0.13.0.tar.gz
	tar xvf PyClone-0.13.0.tar.gz
	
	wget https://gist.githubusercontent.com/markoglasgow/3ebdb8524eb9dfcf41635924a916a0b8/raw/fd5ce4df349919c7478f7d45c43a35535f7b16ec/pyclone_pypy_patch.diff
	patch -p0 -i pyclone_pypy_patch.diff
	
	cd PyClone-0.13.0
	pypy setup.py install
	chmod a+x PyClone
	cd ..
	sudo mv PyClone-0.13.0 /opt
	sudo ln -s /opt/PyClone-0.13.0/PyClone /usr/bin/PyClone
	cd ..
	rm -rf pypy

	# run PyClone to force Matplotlib to build the font cache
	PyClone 

	# Install phylowgs to /opt and make symlinks to its scripts. 
	sudo apt-get install libgsl2 libgsl-dev

	cd ~/Desktop
	mkdir phylowgs
	cd phylowgs/
	git clone https://github.com/markoglasgow/phylowgs.git .
	chmod a+x evolve.py
	chmod a+x write_results.py
	chmod a+x parser/parse_cnvs.py
	chmod a+x parser/create_phylowgs_inputs.py

	g++ -o mh.o -O3 mh.cpp  util.cpp `gsl-config --cflags --libs`

    # Set up the symlinks to PhyloWGS required to run the pipeline script. 
	cd ~/Desktop
	sudo mv phylowgs /opt/phylowgs
	sudo ln -s /opt/phylowgs/evolve.py /usr/bin/PhyloWGS
	sudo ln -s /opt/phylowgs/write_results.py /usr/bin/PhyloWGS_write_results
	sudo ln -s /opt/phylowgs/parser/parse_cnvs.py /usr/bin/PhyloWGS_parse_cnvs
	sudo ln -s /opt/phylowgs/parser/create_phylowgs_inputs.py /usr/bin/PhyloWGS_create_inputs

	# Install PyCharm with Oracle JRE. 
	sudo add-apt-repository ppa:webupd8team/java
	sudo apt-get purge libappstream3
	sudo apt-get update
	sudo apt-get install oracle-java9-installer

	cd ~/Desktop
	wget https://download.jetbrains.com/python/pycharm-community-2017.3.tar.gz
	tar xvf pycharm-community-2017.3.tar.gz
	rm pycharm-community-2017.3.tar.gz

	# Run pycharm and let it create the 'charm' symlink
	/opt/pycharm-community-2017.3/bin/pycharm.sh

	# Install Sublime Text 3
	wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
	sudo apt-get install apt-transport-https
	echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
	sudo apt-get update
	sudo apt-get install sublime-text

	# Set Sublime Text as default text editor. You also need to right click on an application -> Open With -> Open With Other Application -> Select Sublime Text -> check "Use as default for this kind of file"
	echo "export EDITOR='subl'" >> ~/.bashrc
	echo "export VISUAL='subl'" >> ~/.bashrc
	source ~/.bashrc

    # in case of matplotlib bug complaining about Python not being installed as a framework (should only happen on OSX)
    # touch ~/.matplotlib/matplotlibrc
    # echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc


