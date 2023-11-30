import numbers

addition_sign_mapping={(1,1):1,(-1,-1):-1,(1,0):1,(0,1):1,(0,-1):-1,(-1,0):-1,(0,0):0,(1,-1):None,(-1,1):None,
                       (1,None):None,(0,None):None,(-1,None):None,(None,1):None,(None,0):None,(None,-1):None,(None,None):None}
opposite_sign_mapping={1:-1,-1:1,0:0,None:None}
product_sign_mapping={(1,1):1,(-1,-1):1,(1,-1):-1,(-1,1):-1,(1,0):0,(0,1):0,(0,-1):0,(-1,0):0,(0,0):0,
                      (None,0):0,(0,None):0,(1,None):None,(None,1):None,(-1,None):None,(None,-1):None,(None,None):None}
sign_notation_mapping_dict={"+":1,"0":0,"-":-1}



class Sign:
    def __init__(self,value,derivative=False):
        self.value = value
        self.derivative = derivative

        if isinstance(self.value, numbers.Number):
            assert self.value in [-1,0,1]
        elif isinstance(self.value, str):
            assert self.value in ["+","0","-"]
            self.value = sign_notation_mapping_dict[self.value]
        elif self.value==None:
            pass
        else:
            raise ValueError('Value must be a number or one of "+", "-", "0"') #assertion error?

    def __str__(self):
        if isinstance(self.value, numbers.Number):
            if self.value==1:
                if self.derivative==True:
                    return "inc"
                else:
                    return "[+]"
            elif self.value==-1:
                if self.derivative==True:
                    return "dec"
                else:
                    return "[-]"
            elif self.value==0:
                if self.derivative==True:
                    return "std"
                else:
                    return "[0]"
        else:
            return str(None)
            
    def __repr__(self):
        if isinstance(self.value, numbers.Number):
            if self.value==1:
                if self.derivative==True:
                    return "inc"
                else:
                    return "[+]"
            elif self.value==-1:
                if self.derivative==True:
                    return "dec"
                else:
                    return "[-]"
            elif self.value==0:
                if self.derivative==True:
                    return "std"
                else:
                    return "[0]"
        else:
            return str(None)


    def __eq__(self,other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        return self.value==other.value
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __ne__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        return self.value!=other.value

    def __add__(self,other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        return Sign(addition_sign_mapping[(self.value,other.value)])
    
    def __neg__(self):
        return Sign(opposite_sign_mapping[self.value])
    
    def __sub__(self,other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        return Sign(addition_sign_mapping[(self.value,(-other).value)])
    
    def __mul__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        return Sign(product_sign_mapping[(self.value,other.value)])
    
    def __lt__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        if isinstance(self.value,numbers.Number) and isinstance(other.value,numbers.Number):
            return self.value<other.value
        else:
            return None
            
    def __gt__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        if isinstance(self.value,numbers.Number) and isinstance(other.value,numbers.Number):
            return self.value>other.value
        else:
            return None
        
    def __le__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        if isinstance(self.value,numbers.Number) and isinstance(other.value,numbers.Number):
            return self.value<=other.value
        else:
            return None
        
    def __ge__(self, other):
        assert isinstance(other,Sign), "Binary operation supports only instances of Sign"
        if isinstance(self.value,numbers.Number) and isinstance(other.value,numbers.Number):
            return self.value>=other.value
        else:
            return None

    @property
    def is_positive(self):
        if self.value==1:
            return True
        else:
            return False
        
    @property
    def is_negative(self):
        if self.value==-1:
            return True
        else:
            return False
        
    @property
    def is_zero(self):
        if self.value==0:
            return True
        else:
            return False
        
    @property
    def is_derivative(self):
        return self.derivative



class landmark_value:
    def __init__(self,name,input_sign,is_finite=True):
        self.name = name
        self.sign = input_sign
        self.is_finite = is_finite

        if not isinstance(self.sign,Sign):
            self.sign = Sign(self.sign)

        assert isinstance(self.name,str), "Name must be of type str"
        assert isinstance(self.sign,Sign), "Must use a valid sign"
        assert isinstance(self.is_finite,bool)
        
        if self.sign==Sign(0):
            assert self.is_finite, "Zero values must be Finite"
        
    def __str__(self):
        return (self.name)
    
    def __repr__(self):
        return (self.name)
    
    def __eq__(self,other):
        #assert isinstance(other,landmark_value) or isinstance(other,type(None) or isinstance(tuple)), "Binary operation supports only instances of Landmark Values, Tuples or NoneType"
        if isinstance(other,landmark_value):
            return self.name==other.name and self.sign==other.sign and self.is_finite==other.is_finite
        else:
            return False
        
    def __hash__(self):
        return hash((self.name,self.sign,self.is_finite))
    
    def __ne__(self, other):
        #assert isinstance(other,landmark_value) or isinstance(other,type(None) or isinstance(tuple)), "Binary operation supports only instances of Landmark Values, Tuples or NoneType"
        if isinstance(other,landmark_value):
            return self.name!=other.name or self.sign!=other.sign or self.is_finite!=other.is_finite
        else:
            return True



class quantity_space:
    def __init__(self,variable,landmarks_list):
        self.variable = variable
        self.landmarks = landmarks_list
        self._minimum_limit = landmarks_list[0] #landmark_value("-inf",-1,is_finite=False)
        self._maximum_limit = landmarks_list[-1] #landmark_value("inf",1,is_finite=False)
        #self.state = state
        assert all([isinstance(l,landmark_value) for l in self.landmarks]), "Quantity Space must be made of a list of landmark values"
        
    def __str__(self):
        #return self.variable+" "+str([l.name for l in self.landmarks])
        return self.variable+": "+" ... ".join([str(l.name) for l in self.landmarks])
    
    def __repr__(self):
        return self.variable+": "+" ... ".join([str(l.name) for l in self.landmarks])
    
    def __eq__(self,other):
        #assert isinstance(other,quantity_space)
        if other==None:
            return False
        else:
            return self.variable==other.variable and self.landmarks==other.landmarks and self._minimum_limit==other._minimum_limit and self._maximum_limit==other._maximum_limit
        
    def __hash__(self) -> int: #include max and min limits? might cause conflict if limits are changed
        return hash((self.variable,tuple(self.landmarks)))
    
    @property
    def names(self):
        #assert names are all strings 
        #assert names are all unique #assert len(self.names)!=len(set(self.names))
        return [l.name for l in self.landmarks]
    
    @property
    def signs(self):
        signs_list=[l.sign for l in self.landmarks]

        #assert list is sorted in ascending order
        assert all(signs_list[i] <= signs_list[i+1] for i in range(len(signs_list)-1)), "signs of landmarks are not in proper order"
        
        assert Sign(None) not in signs_list, "can't have none signs in a quantity space"
        
        return signs_list
    
    @property
    def length(self):
        return len(self.landmarks)
    
    @property
    def has_zero(self):
        #assert there is only one zero
        return Sign(0) in self.signs
    
    @property
    def has_pos_infinity(self):
        #assert there is only one positive inf at most
        return True in [(not l.is_finite) and l.sign==Sign(1) for l in self.landmarks]
    
    @property
    def has_neg_infinity(self):
        #assert there is only one negative inf at most
        return True in [(not l.is_finite) and l.sign==Sign(-1) for l in self.landmarks]
    
    @property
    def has_any_infinity(self):
        return self.has_pos_infinity or self.has_neg_infinity
    

    #to modify default limit values, insert value, then set limit
    
    @property
    def minimum_limit(self):
        return self._minimum_limit
    
    #@minimum_limit.setter
    def set_minimum_limit(self,value=None):
        if type(value) not in [landmark_value,type(None)]:
            raise ValueError("Value Entered is not a Qualitative Value")
        if isinstance(value,landmark_value) and value not in self.landmarks:
            raise ValueError("Landmark not in Quantity Space")
        
        if isinstance(value,landmark_value):
            if self.landmarks.index(value)!=0:
                raise ValueError("Minimum Limit is not first Landmark in Quantity Space") #assertion error?
            else:
                self._minimum_limit=value
        else:
            if self.has_neg_infinity==True and (self.landmarks[0].is_finite==True or self.landmarks[0].sign!=-1):
                raise ValueError("Minimum Limit is not first Landmark in Quantity Space") #assertion error?
            self._minimum_limit=self.landmarks[0] 
        
        return self._minimum_limit
 

    @property
    def maximum_limit(self):
        return self._maximum_limit
    
    
    def set_maximum_limit(self,value=None):
        if type(value) not in [landmark_value,type(None)]:
            raise ValueError("Value Entered is not a Qualitative Value")
        if isinstance(value,landmark_value) and value not in self.landmarks:
            raise ValueError("Landmark not in Quantity Space")
        
        if isinstance(value,landmark_value):
            if self.landmarks.index(value)!=len(self.landmarks)-1:
                raise ValueError("Maximum Limit is not last Landmark in Quantity Space") #assertion error?
            else:
                self._maximum_limit=value
        else:
            if self.has_pos_infinity==True and (self.landmarks[-1].is_finite==True or self.landmarks[-1].sign!=1):
                raise ValueError("Maximum Limit is not last Landmark in Quantity Space") #assertion error?
            self._maximum_limit=self.landmarks[-1] 
        
        return self._maximum_limit

    def compare_landmarks(self,landmark1: landmark_value,landmark2: landmark_value):
        #assert type(landmark1)==landmark_value, f"First value is not a Landmark Value"
        #assert type(landmark2)==landmark_value, f"Second value is not a Landmark Value"
        assert landmark1 in self.landmarks, f"First Landmark not in Quantity Space"
        assert landmark2 in self.landmarks, f"Second Landmark not in Quantity Space"
        index1=self.landmarks.index(landmark1)
        index2=self.landmarks.index(landmark2)
        
        if index1==index2:
            return Sign(0)
        elif index1>index2:
            return Sign(1)
        else:
            return Sign(-1)
        


class qualitative_value:
    def __init__(self,qmag,qdir):
        self.qmag = qmag
        self.qdir = qdir
        #self.q_space = q_space
        
        if not isinstance(self.qdir,Sign):
            self.qdir = Sign(self.qdir)
        
        if self.qdir.derivative==False:
            self.qdir.derivative=True


        assert isinstance(self.qdir,Sign) and self.qdir.derivative==True, "Invalid qdir"

        case1 = isinstance(self.qmag,landmark_value) #qmag is only a landmark
        case2 = isinstance(self.qmag,tuple) and len(self.qmag)==2 and type(self.qmag[0])==landmark_value and type(self.qmag[1])==landmark_value #interval between landmarks
        case3 = (self.qmag==None)

        # if self.q_space!=None:
        #     assert isinstance(self.q_space,quantity_space), "Must be a quantity space instance"
        #     case1 = case1 and (self.qmag in self.q_space.landmarks)
        #     case2 = case2 and ( self.q_space.landmarks.index(self.qmag[1])-self.q_space.landmarks.index(self.qmag[0]) ) == 1
        
        assert case1 or case2 or case3, "Invalid qmag"

        #assert qualitative value tuples have contiguous landmarks if q_sapce is provided

    def __str__(self):
        return  "⟨"+str(self.qmag) +", "+str(self.qdir)+"⟩"
        
    
    def __repr__(self):
        return  "⟨"+str(self.qmag) +", "+str(self.qdir)+"⟩"
        
    def __eq__(self, other) -> bool:
        #assert isinstance(other,qualitative_value), "Binary comparison only accepts Qualitative Values"
        if not isinstance(other,qualitative_value):
            return False
        # elif self.q_space!=None or other.q_space!=None:
        #     return self.qmag==other.qmag and self.qdir==other.qdir and self.q_space==other.q_space
        else:
            return self.qmag==other.qmag and self.qdir==other.qdir
        
    def __hash__(self) -> int:
        # if self.q_space!=None:
        #     return hash((self.qmag,self.qdir,self.q_space))
        #     #return self.qmag==other.qmag and self.qdir==other.qdir and self.q_space==other.q_space
        # else:
        return hash((self.qmag,self.qdir))
            #return self.qmag==other.qmag and self.qdir==other.qdir

    @property
    def is_complete(self):
        return self.qmag!=None and self.qdir!=Sign(None)
    
    # @property
    # def variable(self):
    #     if self.q_space!=None:
    #         return self.q_space.variable
    #     else:
    #         return None
        
    @property    
    def qmag_type(self):
        return type(self.qmag)
    
    @property
    def is_finite(self):
        if self.qmag_type==tuple:
            return True
        elif self.qmag==None:
            return None
        elif self.qmag_type==landmark_value:
            return self.qmag.is_finite
        else: 
            raise ValueError("Invalid Qmag")
    
    @property
    def sign(self):
        if self.qmag_type==landmark_value:
            return self.qmag.sign
        elif self.qmag==None:
            return Sign(None)
        else: #tuple
            sign1=self.qmag[0].sign
            sign2=self.qmag[1].sign
            assert sign1!=Sign(0) or sign2!=Sign(0), "Both quantities cannot have a zero sign"
            assert sign1!=-sign2, "Signs of both quantities cannot be opposites, use zero landmark"
            assert sign1<=sign2, "Signs must respect the interval representation"

            if sign1!=Sign(0): #negative or positive interval
                return sign1
            else:
                return sign2 #should be positive
    
    def is_in_q_space(self, q_space: quantity_space):
        if self.qmag_type==landmark_value:
            return self.qmag in q_space.landmarks
        elif self.qmag_type==tuple:
            assert (q_space.landmarks.index(self.qmag[1])-q_space.landmarks.index(self.qmag[0])) == 1, "invalid interval qmag for the provided quantity space"
            return self.qmag[0] in q_space.landmarks and self.qmag[1] in q_space.landmarks
        else:
            raise ValueError("Invalid Qmag type")
            

    def sign_wr_value(self,other,q_space: quantity_space): #included here to be able to compare qualitative value intervals
        #assert isinstance(other,qualitative_value), "Can only make comparison between qualitative values"
        #assert self.q_space!=None and other.q_space!=None, "Values must have a quantity space assigned for comparison"
        assert self.qmag!=None and other.qmag!=None, "Qmag values can't be null values when comparing signs"

        if self.qmag_type==landmark_value:
            x_small= self.qmag
            x_large = x_small
        else:
            assert (q_space.landmarks.index(self.qmag[1])-q_space.landmarks.index(self.qmag[0])) == 1, "invalid interval qmag x"
            x_small= self.qmag[0]
            x_large = self.qmag[1]

        if other.qmag_type==landmark_value:
            y_small= other.qmag
            y_large = y_small
        else:
            assert (q_space.landmarks.index(other.qmag[1])-q_space.landmarks.index(other.qmag[0])) == 1, "invalid interval qmag y"
            y_small= other.qmag[0]
            y_large = other.qmag[1]

        #assert all([l in q_space.landmarks for l in [x_small,x_large,y_small,y_large]]), "Value not in Quantity Space"
        xl_ys_comparison = q_space.compare_landmarks(x_large,y_small)
        yl_xs_comparison = q_space.compare_landmarks(y_large,x_small)
        

        if xl_ys_comparison<Sign(0): #or (self.q_space.compare_landmarks(x_large,y_small)==Sign(0) and y_small!=y_large):
            return Sign(-1)
        elif yl_xs_comparison<Sign(0): #or (self.q_space.compare_landmarks(y_large,x_small)==Sign(0) and x_small!=x_large): 
            return Sign(1)
        elif xl_ys_comparison==Sign(0):
            if y_small!=y_large or x_large!=x_small:
                return Sign(-1)
            else:
                return Sign(0)
        elif yl_xs_comparison==Sign(0):
            if y_small!=y_large or x_large!=x_small:
                return Sign(1)
            else:
                return Sign(0) 
        elif y_large==x_large and y_small==x_small:
            return Sign(0)
        else:
            raise ValueError("Invalid Comparison")

    def sign_wr_infinity(self):
        assert self.qmag!=None, "Qmag values can't be null values when comparing signs"

        if self.qmag_type==tuple:
            return Sign(0)
        elif self.qmag.is_finite:
            return Sign(0)
        elif self.qmag.sign==Sign(1):
            return Sign(1)
        elif self.qmag.sign==Sign(-1):
            return Sign(-1)
        else:
            raise ValueError("Invalid Qmag")
        
      #return np.sign(x)
        
    def sign_log_abs_wr_infinity(self):
        #f(x)=log|x|_inf
        #x=0, f(x)=-1
        #x neq 0 and finite, f(x)=0
        #x=pm infty, f(x)=1
        assert self.qmag!=None, "Qmag values can't be null values when comparing signs"

        if self.is_finite and self.sign==Sign(0):
            return Sign(-1)
        elif self.is_finite and self.sign!=Sign(0):
            return Sign(0)
        elif not self.is_finite:
            return Sign(1)
        else:
            raise ValueError("Invalid Qmag")
    
        
    def sign_abs_wr_value_abs(self,other,q_space: quantity_space):
        #[|x|]_|x_i| evaluate only when sign is the same
        assert isinstance(other,qualitative_value), "Can only make comparison between qualitative values"
        #assert self.q_space!=None and other.q_space!=None, "Values must have a quantity space assigned for comparison"
        assert self.qmag!=None and other.qmag!=None, "Qmag values can't be null values when comparing signs"


        if self.sign!=-other.sign: #should be None value
            if self.sign==Sign(1) or other.sign==Sign(1):
                return self.sign_wr_value(other,q_space=q_space)
            elif self.sign==Sign(-1) or other.sign==Sign(-1):
                return -self.sign_wr_value(other,q_space=q_space)
            else:
                raise ValueError("Invalid Qmag")
        else: #sign of x and x_i are opposites, no way to compare their values in general cases
            return Sign(None)


class Qualitative_State(dict): #makes the class inherit properties and methods from the dict class
    def __init__(self,state_dict: dict,**kwargs):
        self.state = state_dict
        
        super(Qualitative_State,self).__init__(state_dict,**kwargs) #initiates dict class instance as a parent class
        #assert isinstance(self.state,dict), "State must be a dictionary"
        
        self.variables = list(self.keys())
        self.q_values = list(self.values())
        assert all([isinstance(qv,qualitative_value) for qv in self.q_values]), "Values must be Qualitative Values"

        #self.reference_vars = reference_vars

    #@property
    def is_quiescent(self,time_var=None): #steady state
        if time_var==None:
            return all([qv.qdir==Sign(0) for qv in self.q_values])
        else:
            return all([self.state[var].qdir==Sign(0) for var in self.variables if var!=time_var])

    #@property
    def is_complete(self,reference_vars=None): #state vars 
        if reference_vars!=None:
            #return all([qv.is_complete for qv in self.q_values if (qv.variable in reference_vars)]) #and set(self.variables)==set(reference_vars)
            return all([self.state[var].is_complete for var in reference_vars])
        else:
            return all([qv.is_complete for qv in self.q_values])
        

def possible_values_from_qs(x_qs: quantity_space): 
    # min_lim=x_qs.minimum_limit
    # max_lim=x_qs.maximum_limit
    
    q_vals=x_qs.landmarks
    
    p_values=[]
    for qv in q_vals:
        # if (qv.is_finite==False and qv.sign==Sign(1)) or qv==max_lim: #+inf or max
        #     q_dirs=[-1,0]
        # elif (qv.is_finite==False and qv.sign==Sign(-1)) or qv==min_lim: #-inf or min
        #     q_dirs=[0,1]
        # else:
        q_dirs=[-1,0,1]
        q_dirs=[Sign(qd,derivative=True) for qd in q_dirs]
        #print(qv)
        p_values.extend([qualitative_value(qv,qd) for qd in q_dirs])
    
    i_values=[]
    for i in range(len(q_vals)-1):
        q_dirs=[-1,0,1]
        q_dirs=[Sign(qd,derivative=True) for qd in q_dirs]
        qmag=(q_vals[i],q_vals[i+1])
        i_values.extend([qualitative_value(qmag,qd) for qd in q_dirs ])
    
    return p_values,i_values


def domain_restriction(Q,Dbar=None) -> dict: #Q: quantity spaces, Dbar: state with partial info
    """
    returns intersection of restricted domain Dbar and total domain (from possible values from the QS)
    """
    if type(Q)==dict:
        Q=list(Q.values())

    Domains={}
    for qs in Q:
        variable=qs.variable
        valid_qvs=[]
        for qv in possible_values_from_qs(qs)[0]+possible_values_from_qs(qs)[1]:
            valid_qmag=False
            valid_qdir=False

            if Dbar!=None and variable in Dbar.keys(): #the partial state (Dbar) has data from the same variable

                #if isinstance(qv.qmag,landmark_value):
                if Dbar[variable].qmag==None or (Dbar[variable].qmag==qv.qmag and qs.variable==variable):
                    valid_qmag=True

                #else: #qs.qmag is tuple
                #    if Dbar[variable].qmag==None or (isinstance(Dbar[variable],tuple) and Dbar[variable].qmag==qv.qmag and qs.variable==variable):
                #        valid_qmag=True

                if qv.qdir==Dbar[variable].qdir or Dbar[variable].qdir == Sign(None):
                    valid_qdir=True

                #print(Dbar[variable].qmag,qv.qmag, valid_qmag)
                #print(Dbar[variable].qdir,qv.qdir, valid_qdir)
            else:
                valid_qmag=True
                valid_qdir=True
            
            if valid_qdir and valid_qmag:
                valid_qvs.append(qv)

        Domains[variable]=valid_qvs

    return Domains