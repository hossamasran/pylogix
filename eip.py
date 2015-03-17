from struct import *
from random import randrange
import socket
import sys
import ctypes

self=None
PLC=self
class Self():
    pass
  
def __init__():
    global self
    global PLC
    
    self=Self()
    PLC=self
    self.IPAddress=""
    self.Port=44818
    self.Context='Rad'
    self.CIPDataTypes={"STRUCT":(0,0x02A0,'B'),"BOOL":(1,0x00C1,'?'),"SINT":(1,0x00C2,'b'),"INT":(2,0x00C3,'h'),"DINT":(4,0x00C4,'i'),"REAL":(4,0x00CA,'f'),"DWORD":(4,0x00D3,'I'),"LINT":(8,0x00C5,'Q')}
    self.CIPDataType=None
    self.CIPData=None
    self.VendorID=0x1234
    self.SerialNumber=randrange(65000)
    self.OriginatorSerialNumber=42
    self.Socket=socket.socket()
    self.SessionHandle=0x0000
    self.OTNetworkConnectionID=None
    self.TagName=None
    self.Offset=None
    self.NumberOfElements=1
    self.SequenceCounter=0
    self.CIPRequest=None
    self.Socket.settimeout(0.5)
    self.Offset=None
    self.Offset2=None
    self.ReceiveData=None
    self.ForwardOpenDone=False
    self.RegisterSesionDone=False
    self.SocketConnected=False
    PLC=self

  
def _openconnection():
    self.SocketConnected=False
    try:    
        self.Socket=socket.socket()
        self.Socket.settimeout(0.5)
        self.Socket.connect((self.IPAddress,self.Port))
        self.SocketConnected=True
    except:
        #print "open except ",sys.exc_info()
        self.SocketConnected=False
    return
  
def _buildRegisterSession():
    EIPCommand=0x0065                       #(H)Register Session Command   (Vol 2 2-3.2)
    EIPLength=0x0004                        #(H)Lenght of Payload          (2-3.3)
    EIPSessionHandle=self.SessionHandle     #(I)Session Handle             (2-3.4)
    EIPStatus=0x0000                        #(I)Status always 0x00         (2-3.5)
    EIPContext=self.Context                 #(8s)                          (2-3.6)
    EIPOptions=0x0000                       #(I)Options always 0x00        (2-3.7)
                                            #Begin Command Specific Data
    EIPProtocolVersion=0x01                 #(H)Always 0x01                (2-4.7)
    EIPOptionFlag=0x00                      #(H)Always 0x00                (2-4.7)

    self.registersession=pack('<HHII8sIHH',
                              EIPCommand,
                              EIPLength,
                              EIPSessionHandle,
                              EIPStatus,
                              EIPContext,
                              EIPOptions,
                              EIPProtocolVersion,
                              EIPOptionFlag)
    return
  
def _buildUnregisterSession():
    EIPCommand=0x66
    EIPLength=0x00
    EIPSessionHandle=self.SessionHandle
    EIPStatus=0x00
    EIPContext=self.Context
    EIPOptions=0x00

    self.unregistersession=pack('<HHII8sI',
                                EIPCommand,
                                EIPLength,
                                EIPSessionHandle,
                                EIPStatus,
                                EIPContext,
                                EIPOptions)
    return
  
def _buildForwardOpenPacket():
    _buildCIPForwardOpen()
    _buildEIPSendRRDatHeader()
    self.ForwardOpenFrame=self.EIPSendRRFrame+self.CIPForwardOpenFrame
    return
  
def _buildEIPSendRRDatHeader():
    EIPCommand=0x6F                                 #(H)EIP SendRRData         (Vol2 2-4.7)
    EIPLength= 16+len(self.CIPForwardOpenFrame)     #(H)
    EIPSessionHandle=self.SessionHandle             #(I)
    EIPStatus=0x00                                  #(I)
    EIPContext=self.Context                         #(8s)
    EIPOptions=0x00                                 #(I)
                                                    #Begin Command Specific Data
    EIPInterfaceHandle=0x00                         #(I) Interface Handel       (2-4.7.2)
    EIPTimeout=0x00                                 #(H) Always 0x00
    EIPItemCount=0x02                               #(H) Always 0x02 for our purposes
    EIPItem1Type=0x00                               #(H) Null Item Type
    EIPItem1Length=0x00                             #(H) No data for Null Item
    EIPItem2Type=0xB2                               #(H) Uconnected CIP message to follow
    EIPItem2Length=len(self.CIPForwardOpenFrame)    #(H)

    self.EIPSendRRFrame=pack('<HHII8sIIHHHHHH',
                             EIPCommand,
                             EIPLength,
                             EIPSessionHandle,
                             EIPStatus,
                             EIPContext,
                             EIPOptions,
                             EIPInterfaceHandle,
                             EIPTimeout,
                             EIPItemCount,
                             EIPItem1Type,
                             EIPItem1Length,
                             EIPItem2Type,
                             EIPItem2Length)
    return
  
def _buildCIPForwardOpen():
    CIPService=0x54                                  #(B) CIP OpenForward        Vol 3 (3-5.5.2)(3-5.5)
    CIPPathSize=0x02                                 #(B) Request Path zize              (2-4.1)
    CIPClassType=0x20                                #(B) Segment type                   (C-1.1)(C-1.4)(C-1.4.2)
                                                            #[Logical Segment][Class ID][8 bit addressing]
    CIPClass=0x06                                    #(B) Connection Manager Object      (3-5)
    CIPInstanceType=0x24                             #(B) Instance type                  (C-1.1)
                                                            #[Logical Segment][Instance ID][8 bit addressing]
    CIPInstance=0x01                                 #(B) Instance
    CIPPriority=0x0A                                 #(B) Timeout info                   (3-5.5.1.3)(3-5.5.1.2)
    CIPTimeoutTicks=0x0e                             #(B) Timeout Info                   (3-5.5.1.3)
    CIPOTConnectionID=0x20000002                     #(I) O->T connection ID             (3-5.16)
    CIPTOConnectionID=0x20000001                     #(I) T->O connection ID             (3-5.16)
    CIPConnectionSerialNumber=self.SerialNumber      #(H) Serial number for THIS connection (3-5.5.1.4)
    CIPVendorID=self.VendorID                        #(H) Vendor ID                      (3-5.5.1.6)
    CIPOriginatorSerialNumber=self.OriginatorSerialNumber    #(I)                        (3-5.5.1.7)
    CIPMultiplier=0x03                               #(B) Timeout Multiplier             (3-5.5.1.5)
    CIPFiller=(0x00,0x00,0x00)                       #(BBB) align back to word bound
    CIPOTRPI=0x00201234                              #(I) RPI just over 2 seconds        (3-5.5.1.2)
    CIPOTNetworkConnectionParameters=0x43f4          #(H) O->T connection Parameters    (3-5.5.1.1)
						     # Non-Redundant,Point to Point,[reserved],Low Priority,Variable,[500 bytes] 
						     # Above is word for Open Forward and dint for Large_Forward_Open (3-5.5.1.1)
    CIPTORPI=0x00204001                              #(I) RPI just over 2 seconds       (3-5.5.1.2)
    CIPTONetworkConnectionParameters=0x43f4          #(H) T-O connection Parameters    (3-5.5.1.1)
                                                     # Non-Redundant,Point to Point,[reserved],Low Priority,Variable,[500 bytes] 
                                                     # Above is word for Open Forward and dint for Large_Forward_Open (3-5.5.1.1)
    CIPTransportTrigger=0xA3                         #(B)                                   (3-5.5.1.12)
    CIPConnectionPathSize=0x04                       #(B)                                   (3-5.5.1.9)
    CIPConnectionPath=(0x01,0x00,0x20,0x02,0x24,0x01,0x2c,0x01) #(8B) Compressed / Encoded Path  (C-1.3)(Fig C-1.2)

    """
    Port Identifier [BackPlane]
    Link adress 0x00
    Logical Segment ->Class ID ->8-bit
    ClassID 0x02
    Logical Segment ->Instance ID -> 8-bit
    Instance 0x01
    Logical Segment -> connection point ->8 bit
    Connection Point 0x01
    """
    self.CIPForwardOpenFrame=pack('<BBBBBBBBIIHHIB3BIhIhBB8B',
                                  CIPService,
                                  CIPPathSize,
                                  CIPClassType,
                                  CIPClass,
                                  CIPInstanceType,
                                  CIPInstance,
                                  CIPPriority,
                                  CIPTimeoutTicks,
                                  CIPOTConnectionID,
                                  CIPTOConnectionID,
                                  CIPConnectionSerialNumber,
                                  CIPVendorID,
                                  CIPOriginatorSerialNumber,
                                  CIPMultiplier,
                                  CIPFiller[0],CIPFiller[1],CIPFiller[2],           #Very Unclean!!!!!
                                  CIPOTRPI,
                                  CIPOTNetworkConnectionParameters,
                                  CIPTORPI,
                                  CIPTONetworkConnectionParameters,
                                  CIPTransportTrigger,
                                  CIPConnectionPathSize,
                                  CIPConnectionPath[0],CIPConnectionPath[1],CIPConnectionPath[2],CIPConnectionPath[3],
                                  CIPConnectionPath[4],CIPConnectionPath[5],CIPConnectionPath[6],CIPConnectionPath[7])
                                  
                                   
    
    
    return
  
def _buildEIPHeader():

    EIPPayloadLength=22+len(self.CIPRequest)   #22 bytes of command specific data + the size of the CIP Payload
    
    EIPConnectedDataLength=len(self.CIPRequest)+2 #Size of CIP packet plus the sequence counter

    EIPCommand=0x70                         #(H) Send_unit_Data (vol 2 section 2-4.8)
    EIPLength=22+len(self.CIPRequest)       #(H) Length of encapsulated command
    EIPSessionHandle=self.SessionHandle     #(I)Setup when session crated
    EIPStatus=0x00                          #(I)Always 0x00
    EIPContext=self.Context                 #(8s) String echoed back
                                            #Here down is command specific data
                                            #For our purposes it is always 22 bytes
    EIPOptions=0x0000                       #(I) Always 0x00
    EIPInterfaceHandle=0x00                 #(I) Always 0x00
    EIPTimeout=0x00                         #(H) Always 0x00
    EIPItemCount=0x02                       #(H) For our purposes always 2
    EIPItem1ID=0xA1                         #(H) Address (Vol2 Table 2-6.3)(2-6.2.2)
    EIPItem1Length=0x04                     #(H) Length of address is 4 bytes
    EIPItem1=self.OTNetworkConnectionID     #(I) O->T Id
    EIPItem2ID=0xB1                         #(H) Connecteted Transport  (Vol 2 2-6.3.2)
    EIPItem2Length=EIPConnectedDataLength   #(H) Length of CIP Payload

    
    EIPSequence=self.SequenceCounter        #(H)
    self.SequenceCounter+=1
    self.SequenceCounter=self.SequenceCounter%0x10000
    
    self.EIPHeaderFrame=pack('<HHII8sIIHHHHIHHH',
                        EIPCommand,
                        EIPLength,
                        EIPSessionHandle,
                        EIPStatus,
                        EIPContext,
                        EIPOptions,
                        EIPInterfaceHandle,
                        EIPTimeout,
                        EIPItemCount,
                        EIPItem1ID,
                        EIPItem1Length,
                        EIPItem1,
                        EIPItem2ID,EIPItem2Length,EIPSequence)
    self.EIPFrame=self.EIPHeaderFrame+self.CIPRequest
    return

def _buildCIPTagReadRequestSuper():
    """
    Wish me luck!
    So here's what happens here.  Tags can be super simple like mytag or pretty complex
    like My.Tag[7].Value.  In the example, the tag needs to be split up by the '.' and
    assembled different depending on if the portion is an array or not.  The other thing
    we have to consider is if the tag segment is an even number of bytes or not.  If it's
    not, then we have to add a byte.
    
    So throughout this function we have to figure out the number of words necessary
    for this packet as well assemblying the tag portion of the packet.  It might be more
    complicated than it should be but that's all I could come up with.
    """
    RequestPathSize=0	# define path size
    RequestTagData=""		# define tag data
    RequestElements=self.NumberOfElements
    
    TagSplit = self.TagName.lower().split(".")
    
    # this loop figures out the packet length and builds our packet
    for i  in xrange(len(TagSplit)):
    
	if TagSplit[i].endswith("]"):
	    RequestPathSize+=1					# add a word for 0x91 and len
	    ElementPosition=(len(TagSplit[i])-TagSplit[i].index("["))	# find position of [
	    basetag=TagSplit[i][:-ElementPosition]		# remove [x]: result=SuperDuper
	    temp=TagSplit[i][-ElementPosition:]			# remove tag: result=[x]
	    index=int(temp[1:-1])				# strip the []: result=x
	    BaseTagLenBytes=len(basetag)			# get number of bytes
	
	    # Assemble the packet
	    RequestTagData+=pack('<BB', 0x91, len(basetag))	# add the req type and tag len to packet
	    RequestTagData+=basetag				# add the tag name
	    if BaseTagLenBytes%2==1:				# check for odd bytes
		BaseTagLenBytes+=1				# add another byte to make it even
		RequestTagData+=pack('<B', 0x00)		# add the byte to our packet
	    
	    BaseTagLenWords=BaseTagLenBytes/2			# figure out the words for this segment

	    RequestPathSize+=BaseTagLenWords			# add it to our request size
	    if index < 256:					# if index is 1 byte...
		RequestPathSize+=1				# add word for array index
		RequestTagData+=pack('<BB', 0x28, index)	# add one word to packet
	    if index > 255:					# if index is more than 1 byte...
		RequestPathSize+=2				# add 2 words for array for index
		RequestTagData+=pack('<BBH', 0x29, 0x00, index) # add 2 words to packet
	    #print ""
	
	else:
	    # for non-array segment of tag
	    RequestPathSize+=1					# add a word for 0x91 and len
	    BaseTagLenBytes=len(TagSplit[i])			# store len of tag
	    RequestTagData+=pack('<BB', 0x91, len(TagSplit[i]))	# add to packet
	    RequestTagData+=TagSplit[i]				# add tag req type and len to packet
	    if BaseTagLenBytes%2==1:				# if odd number of bytes
		BaseTagLenBytes+=1				# add byte to make it even
		RequestTagData+=pack('<B', 0x00)		# also add to packet
	    RequestPathSize+=BaseTagLenBytes/2			# add words to our path size

    #print "Total Words:", TotalWords
    # start assembling the results!
    RequestService=0x4C			#CIP Read_TAG_Service (PM020 Page 17)
    CIPReadRequest=pack('<BB', RequestService, RequestPathSize)	# beginning of our req packet
    CIPReadRequest+=RequestTagData				# Tag portion of packet
    CIPReadRequest+=pack('<H', RequestElements)			# end of packet
    self.CIPRequest=CIPReadRequest	
    return
    
def _buildCIPTagReadRequestStuffs():
    '''
    What I have here is what we call a cluster fuck.  Might be necessary but a cluster 
    fuck none the less.  The packet needs to be assembled different ways depending on if
    you are reading a normal tag, array or UDT (SuperDuper, SuperDuper[x], Super.Duper)
    
    First off by using the split, we can determine if it's a UDT becaues they contain "."
    
    Also, if we look for a ] at the end, then we are working with an array.  Arrays are silly
    because we have to pass the tag without the [x] on it.  We also have to pass it the index
    in [x] (we pass it x).  So because of this, I have to figure the length different
    
    There's probably a cleaner way to do this but I just barely got it working.
    
    So the following block of code really just figures out the RequestPathSize
    '''
    TagSplit=self.TagName.lower().split(".")	# try splitting in case we're reading a UDT
    
    if self.TagName.endswith("]"):	
	plctag=self.TagName
	# we are after an array, let's pretend SuperDuper[x]
	ElementPosition=(len(plctag)-plctag.index("["))	# find position of [
	basetag=plctag[:-ElementPosition]		# remove [x]: result=SuperDuper
	temp=plctag[-ElementPosition:]			# remove tag: result=[x]
	index=int(temp[1:-1])				# strip the []: result=x
	TagNamePathLengthBytes=len(basetag)		# get number of bytes
	
	# if it's odd number, add another word
	if TagNamePathLengthBytes%2==1: TagNamePathLengthBytes+=1

	TagNamePathLengthWords=1 			# start with 1 word for 0x91 and tag len
	TagNamePathLengthWords+=int(TagNamePathLengthBytes/2)	# add words for tag name
	
	if index < 256:			# if index < 256, we need 1 word to store the index	
	    TagNamePathLengthWords+=1	# add additional word for index
	else:				# if index > 256 we need 2 words to store index
	    TagNamePathLengthWords+=2	# add 2 words for index
    else:
	BaseTagNameLength=len(self.TagName)	# get the base tag length
	TagNamePadded=self.TagName
	 # add null to put on word boundry
	if (BaseTagNameLength%2): TagNamePadded+=pack('B',0x00)          

	TagNamePath=TagNamePadded
	TagNamePathLengthBytes=len(TagNamePath)
	TagNamePathLengthWords=int(TagNamePathLengthBytes/2)
	TagNamePathLengthWords+=len(TagSplit)

    """
    Now that we figured out the RequestPathSize in probably the most complicated way possible,
    we need to assemble the packet.  Of course it gets assembled in multiple ways
    """
    RequestService=0x4C                             #CIP Read_TAG_Service (PM020 Page 17)
    RequestPathSize=TagNamePathLengthWords          #Lenght of path in words
    RequestElements=self.NumberOfElements
    CIPReadRequest=pack('<BB', RequestService, RequestPathSize)
    
    """
    Here's where we actually assemble the packet for reading the tag.  Again, we have
    different ways of doing this depending on if we are reading SuperDuper, Super.Duper or
    SuperDuper[x].
    
    There are a few if/else statments where we are using %, this is to figure out if something
    is an odd/even number of bytes.  If odd, we need to ad a byte to make sure they are "word friendly"
    """
    if len(TagSplit) > 1:	# assemble tag for UDT
	for i in xrange(len(TagSplit)):
	    # add the service code and name length
	    CIPReadRequest+=pack('<BB', 0x91, len(TagSplit[i]))
	    CIPReadRequest+=TagSplit[i]
	    if len(TagSplit[i])%2==1: CIPReadRequest+=pack('<B', 0x00)	
    elif self.TagName.endswith("]"):	# Assemble differently for array
	# again, add the service code and tag length
	CIPReadRequest+=pack('<BB', 0x91, len(basetag))
	CIPReadRequest+=basetag
	if len(basetag)%2==1: CIPReadRequest+=pack('<B', 0x00)

	# add the index, occupies one word
	if index < 256:	CIPReadRequest+=pack('<BB', 0x28, index)
	# add the index, occupies two words
	if index > 255: CIPReadRequest+=pack('<BBH', 0x29, 0x00, index)
	
    else:	# and for regular o'l tag
	CIPReadRequest+=pack('<BB', 0x91, len(TagSplit[0]))
	CIPReadRequest+=TagSplit[0]
	if len(TagSplit[0])%2==1: CIPReadRequest+=pack('<B', 0x00)

    # the final part of the packet, common for any tag read
    CIPReadRequest+=pack('<H', RequestElements)
    self.CIPRequest=CIPReadRequest
    return


def _buildCIPTagWriteRequest():
    """
    given self.tagname, build up various tagname info
    Lot of redundant steps
    When sending a struct, it is up to you to form it correctly
    writing to a struct is speacial case
    The format becomes:
    Tagname,0xA0,0X02,'H' Sturct identifier,number of structs,[struct data]
    the The struc identifier screws things up
    """

    self.SizeOfElements=self.CIPDataTypes[self.CIPDataType.upper()][0]     #Dints are 4 bytes each
    self.NumberOfElements=len(self.WriteData)            #list of elements to write
    self.NumberOfBytes=self.SizeOfElements*self.NumberOfElements
    

    BaseTagNameLength=len(self.TagName)
    TagNamePadded=self.TagName
    if (BaseTagNameLength%2):
        TagNamePadded+=pack('B',0x00)               #add null to put on word boundry

    TagNamePath=TagNamePadded
    if self.Offset != None :
        #first figure out if this is a list(touple) or an int
        if not hasattr(self.Offset,'__len__'):     #if this does not have len it is an int er something
            TagNamePath=TagNamePath+pack('<HH',
                                         0x0029,        #Indicate type of data to follow
                                         self.Offset)   #Add offset
        else:   #This has len so we will make it muli dim
            Depth=len(self.Offset)
            if Depth>3: Depth=3
            for Dim in xrange(Depth):
                TagNamePath=TagNamePath+pack('<HH',
                                         0x0029,        #Indicate type of data to follow
                                         self.Offset[Dim])   #Add offset
    TagNamePathLengthBytes=len(TagNamePath)
    TagNamePathLengthWords=int(TagNamePathLengthBytes/2)+1
    
    RequestNumberOfElements=self.NumberOfElements
    if self.CIPDataType.upper()=="STRUCT":  #Structs are special
        RequestNumberOfElements=self.StructIdentifier
        
    #Start building the request

    RequestService=0x4D                             #CIP Write_TAG_Service (PM020 Page 17)
    RequestPathSize=TagNamePathLengthWords          #Lenght of path in words
 
    
    RequestElements=self.NumberOfElements
    RequestElementType=self.CIPDataTypes[self.CIPDataType.upper()][1]
    
    CIPReadRequestPart1=pack('<BBBB',
                             RequestService,
                             RequestPathSize,
                             0x91,
                             len(self.TagName))
    CIPReadRequestPart2=TagNamePath                 #Fully formed path to tag
                             


    CIPReadRequestPart3=pack('<HH',
                             RequestElementType,
                             RequestNumberOfElements)
                                 
    self.CIPRequest=CIPReadRequestPart1+CIPReadRequestPart2+CIPReadRequestPart3
    for i in xrange(len(self.WriteData)):
        el=self.WriteData[i]
        self.CIPRequest+=pack('<'+self.CIPDataTypes[self.CIPDataType.upper()][2],el)
        
    return
  
def MakeString(string):
    work=[]
    work.append(0x01)
    work.append(0x00)
    temp=pack('<I',len(string))
    for char in temp:
        work.append(ord(char))
    for char in string:
        work.append(ord(char))
    for x in xrange(len(string),84):
        work.append(0x00)
    return work
  
def OpenConnection(IPAddress):
    self.SocketConnected=False
    self.IPAddress=IPAddress
    try:
        _openconnection()
    except:
        print "Failed to open socket"
        print "Fail need something else to do"
        print "Unexpected error:", sys.exc_info()
        return
    self.SerialNumber=self.SerialNumber+1
    if self.SocketConnected==True:
        _buildRegisterSession()
        self.Socket.send(self.registersession)
        self.ReceiveData=self.Socket.recv(1024)
        self.SessionHandle=unpack_from('<I',self.ReceiveData,4)[0]
        self.RegisterSessionDone=True
        
        #try a forward open
        _buildCIPForwardOpen
        _buildForwardOpenPacket()
        self.Socket.send(self.ForwardOpenFrame)
        self.ReceiveData=self.Socket.recv(1024)
        TempID=unpack_from('<I', self.ReceiveData, 44)
        self.OTNetworkConnectionID=TempID[0]
        self.OpenForwardSessionDone=True
        
def ReadStuffs(*args):
    """
     Reads any data type.  We use the args so that the user can either send just a
    	tag name or a tag name and length (for reading arrays)
    
    args[0] = tag name
    args[1] = Number of Elements
    """
    name=args[0]
    PLC.TagName=name
    if len(args) == 2:	# array read
	NumberOfElements=args[1]
	Array=[0 for i in range(NumberOfElements)]   #create array
    else:
	NumberOfElements=1  # if non array, then only 1 element
	
    PLC.NumberOfElements=NumberOfElements
    PLC.Offset=None
    #_buildCIPTagReadRequestStuffs()
    _buildCIPTagReadRequestSuper()
    _buildEIPHeader()
    
    PLC.Socket.send(PLC.EIPFrame)
    PLC.ReceiveData=PLC.Socket.recv(1024)
    
    # extract some status info
    Status=unpack_from('<h',PLC.ReceiveData,46)[0]
    ExtendedStatus=unpack_from('<h',PLC.ReceiveData,48)[0]
    DataType=unpack_from('<h',PLC.ReceiveData,50)[0]
    returnvalue=0
    
    # if we successfully read from the PLC...
    if Status==204 and ExtendedStatus==0: # nailed it!
	if len(args) == 1:	# user passed 1 argument (non array read)
	    # Do different stuff based on the returned data type
	    if DataType==0:
		# 0 means something wrong with the datatype
		print "Invalid DataTpe", DataType
	    elif DataType==672:
		# gotta handle strings a little different
		NameLength=unpack_from(PackFormat(DataType) ,PLC.ReceiveData, 54)[0]
		returnvalue=PLC.ReceiveData[-84:(-84+NameLength)]
	    else:
		# this handles SINT, INT, DINT, REAL
		returnvalue=unpack_from(PackFormat(DataType), PLC.ReceiveData, 52)[0]
	      
	    return returnvalue

	else:	# user passed more than one argument (array read)
	    for i in xrange(NumberOfElements):
		index=52+(i*BytesPerElement(DataType))
		Array[i]=unpack_from(PackFormat(DataType),PLC.ReceiveData,index)[0]
		    
	    return Array
    else: # didn't nail it
	print Status, ExtendedStatus
	print "Did not nail it, read fail", name
      
def WriteStuffs(*args):
    TagName=args[0]
    Value=args[1]
    DataType=args[2]
    
    PLC.TagName=TagName
    if len(args)==3: PLC.NumberOfElements=1
    if len(args)==4: PLC.NumberOfElements=args[3]

    PLC.Offset=None
    PLC.CIPDataType=DataType
    PLC.WriteData=[]
    if len(args)==3:
	if DataType=="REAL":
	    PLC.WriteData.append(float(Value))
	elif DataType=="STRUCT":
	    PLC.StructIdentifier=0x0fCE
	    PLC.WriteData=MakeString(Value)
	else:
	    PLC.WriteData.append(int(Value))
    elif len(args)==4:
	for i in xrange(PLC.NumberOfElements):
	    PLC.WriteData.append(int(Value[i]))		  
    else:
	print "fix this"
	
    _buildCIPTagWriteRequest()
    _buildEIPHeader()
    PLC.Socket.send(PLC.EIPFrame)
    PLC.ReceiveData=PLC.Socket.recv(1024)


def BytesPerElement(DataType):
    if DataType==193:
	return 1
    elif DataType==194:
	return 1
    elif DataType==195:
	return 2
    elif DataType==196:
	return 4
    elif DataType==202:
	return 4
    elif DataType==672:
	return 4

def PackFormat(DataType):
    if DataType==193:
	return '<?'
    elif DataType==194:
	return '<b'
    elif DataType==195:
	return '<h'
    elif DataType==196:
	return '<i'
    elif DataType==202:
	return '<f'
    elif DataType==672:
	return '<L'