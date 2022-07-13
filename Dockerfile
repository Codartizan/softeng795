FROM python:3.8-slim-buster

#Upgrade pip, install Git & VNC 	
RUN pip install --upgrade pip \
        && apt-get update \
	&& apt-get install -y git x11vnc 
 
# Add entrypoint.sh and other available files to image
ADD . /usr/tims
 
#Change directory and clone Qxf2 Public POM repo
RUN cd /usr/tims \
	&& git clone https://github.com/Codartizan/softeng795.git
 
#Set envirnmental variable for display	
ENV DISPLAY :20
 
#Set working directory
WORKDIR /usr/tims/softeng795
 
##Install requirements using requirements.txt
#RUN pip install -r requirements.txt
 
#Provide read, write and execute permissions for entrypoint.sh and also take care of '\r' error which raised when someone uses notepad or note++ for editing in Windows.
RUN chmod 755 /usr/tims/entrypoint.sh \
	&& sed -i 's/\r$//' /usr/tims/entrypoint.sh
 
#Expose port 5920 to view display using VNC Viewer
EXPOSE 5920
 
#Execute entrypoint.sh at start of container
ENTRYPOINT ["/usr/tims/entrypoint.sh"]