"""
module __Tools__: Base class to construct pore network tools
==================================================================

.. warning:: The classes of this module should be loaded through the 'Base.__init__.py' file.

"""

import sys, os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys.path[1] != parent_dir:
    sys.path.insert(1, parent_dir)
import scipy as sp
import OpenPNM
from OpenPNM.Utilities import Base

class Tools(Base):
    r'''
    This class contains tools to read and write data in OpenPNM objects

    '''
    def __init__(self, **kwargs):
        r'''
        Initialize
        '''
        super(Tools,self).__init__(**kwargs)
        self._logger.info("Construct Base class from Tools subclass")
        #Initialize network properties dictionaries
        self._pore_data = {}
        self._pore_info = {}
        self._throat_data = {}
        self._throat_info = {}
        self._logger.debug("Construction of Tools class complete")
        
    #--------------------------------------------------------------------------
    '''Setter and Getter Methods'''
    #--------------------------------------------------------------------------
    def _set_data(self,element='',prop='',data='',locations='',mode='merge'):
        r'''
        Documentation for this method is being updated, we are sorry for the inconvenience.
        '''
         
        if mode=='remove':
            if data=='':
                try: 
                    getattr(self,'_'+element+'_data')[prop]
                    if locations!='':   
                        getattr(self,'_'+element+'_data')[prop][locations] = sp.nan
                        self._logger.debug('For the '+element+' property '+prop+', the specified data have been deleted in '+self.name)                        
                    else:
                        del getattr(self,'_'+element+'_data')[prop]
                        self._logger.debug(element+' property '+prop+' has been deleted from the dictionary in '+self.name)
                except: self._logger.error(element+' property '+prop+' in '+self.name+' has not been defined. Therefore, no data can be removed!')                              
                
            else:   self._logger.error('For the '+element+' property '+prop+' in '+self.name+': The (remove) mode, will remove the property from the dictionary or specified locations. No data should be sent!')        
        else:
            data = sp.array(data,ndmin=1)
            if data.ndim > 1: data = data.squeeze()
            if 'OpenPNM.Network' in str(self.__class__): net = self
            else: net = self._net
            if type(locations)==list:
                try: locations = getattr(net,'get_'+element+'_indices')(locations)
                except: locations = sp.array(locations,ndmin=1)
            elif type(locations)==sp.ndarray:
                try: locations = getattr(net,'get_'+element+'_indices')(locations)
                except: pass
            elif locations!='':
                try: locations = locations.name
                except: pass
                if type(locations)==str: locations = getattr(net,'get_'+element+'_indices')([locations])
            try: 
                getattr(self,'_'+element+'_data')[prop]
                temp_word = 'updated for '
            except: temp_word = 'added to '            
            if sp.shape(data)[0]==1:
                if locations!='':                
                    try: 
                        getattr(self,'_'+element+'_data')[prop]
                        if mode=='overwrite':
                            getattr(self,'_'+element+'_data')[prop] = sp.zeros((getattr(self,'num_'+element+'s')(),))*sp.nan
                        elif mode=='merge' and sp.shape(getattr(self,'_'+element+'_data')[prop])[0]==1:
                            getattr(self,'_'+element+'_data')[prop] = getattr(self,'_'+element+'_data')[prop]*sp.ones((getattr(self,'num_'+element+'s')(),))
                    except: getattr(self,'_'+element+'_data')[prop] = sp.zeros((getattr(self,'num_'+element+'s')(),))*sp.nan
                    getattr(self,'_'+element+'_data')[prop][locations] = data
                    self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)
                else:
                    try: 
                        getattr(self,'_'+element+'_data')[prop]
                        if mode=='overwrite':
                            if sp.shape(getattr(self,'_'+element+'_data')[prop])[0]!=1:
                                self._logger.debug(element+' property '+prop+' in '+self.name+' was an array which has been overwritten with a scalar value')
                            getattr(self,'_'+element+'_data')[prop] = data
                            self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)
                        if mode=='merge' and sp.shape(getattr(self,'_'+element+'_data')[prop])[0]!=1:  
                            self._logger.error('a scalar data without specified locations cannot be merged into the '+element+' property '+prop+' in '+self.name+' which is (1*N) array. To do so, choose overwrite mode.')
                    except:
                        getattr(self,'_'+element+'_data')[prop] = data
                        self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)
            else:                
                if locations!='':
                    if sp.shape(locations)[0]==sp.shape(data)[0]:
                        try:                                 
                            getattr(self,'_'+element+'_data')[prop]
                            if mode=='overwrite':
                                getattr(self,'_'+element+'_data')[prop] = sp.zeros((getattr(self,'num_'+element+'s')(),))*sp.nan
                        except: getattr(self,'_'+element+'_data')[prop] = sp.zeros((getattr(self,'num_'+element+'s')(),))*sp.nan                            
                        getattr(self,'_'+element+'_data')[prop][locations] = data
                        self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)
                    else: self._logger.error('For adding '+element+' property '+prop+' to '+self.name+', locations and size of data do not match!')
                else:
                    try: 
                        getattr(self,'num_'+element+'s')()                        
                        if sp.shape(data)[0]==getattr(self,'num_'+element+'s')():
                            getattr(self,'_'+element+'_data')[prop] = data
                            self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)
                        else: self._logger.error('For adding '+element+' property '+prop+' to '+self.name+', no locations have been specified. Also size of the data and number of '+element+'s do not match! To add this property, specify locations or change the size of the data.')
                    except: 
                        getattr(self,'_'+element+'_data')[prop] = data
                        self._logger.debug(element+' property '+prop+' has been '+temp_word+self.name)

    def _get_data(self,element='',prop='',locations='',mode=''):
        r'''
        Documentation for this method is being updated, we are sorry for the inconvenience.
        '''
        if self.__module__.split('.')[1] == 'Network': net = self
        else: net = self._net
        if type(locations)==list: 
            try: locations = getattr(net,'get_'+element+'_indices')(locations)
            except: locations = sp.array(locations,ndmin=1)
        elif type(locations)==sp.ndarray:
            try: locations = getattr(net,'get_'+element+'_indices')(locations)
            except: pass            
        elif locations!='':
            try: locations = locations.name 
            except: pass
            if type(locations)==str: locations = getattr(net,'get_'+element+'_indices')([locations])    
        if locations!='':
            if mode != '':
                if mode == 'interpolate':
                    if element == 'pore':
                        return getattr(self,'interpolate_data')(prop=prop,pores=locations)
                    else:
                        return getattr(self,'interpolate_data')(prop=prop,throats=locations)
                else:
                    self._logger.error('The requested mode '+mode+' is not valid')
            else:
                try: 
                    getattr(self,'_'+element+'_data')[prop]
                    try: 
                        if  sp.shape(getattr(self,'_'+element+'_data')[prop])[0]==1 and max(locations)<getattr(self,'num_'+element+'s')():
                            return getattr(self,'_'+element+'_data')[prop]                        
                        else: return getattr(self,'_'+element+'_data')[prop][locations]
                    except: self._logger.error('data for these locations cannot be returned')
                except: 
                    self._logger.error(self.name+' does not have the requested '+element+' property: '+prop) 
        else:
            try: return getattr(self,'_'+element+'_data')[prop]
            except: self._logger.error(self.name+' does not have the requested '+element+' property: '+prop)           
 
    def get_data(self,prop='',pores=[],throats=[],mode=''):
        r'''
        Retrieves data from the object to which it is associated according to 
        input arguments.
        
        Parameters
        ----------
        prop : string
            Name of property to retrieve
        pores : array_like, or string 'all'
            List of pore indices from which to retrieve data.  If set to 'all',
            then ALL values are returned
        throats : array_like, or string 'all'
            List of throat indies from which to retrieve data.  If set to 'all'
            , then ALL values are returned.
        modes : string
            None yet

        Returns
        -------
        array_like
            An ndarray containing the requested property data from the 
            specified locations
            
        See Also
        --------
        get_info

        Notes
        -----
        This is a wrapper method that calls _get_data.  
        Only one of pores or throats should be sent.
            
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> pn.set_data(prop='test',pores=[0],data=1.1)
        >>> pn.get_data(prop='test',pores=[0])
        array([ 1.1])
        '''
        if pores != []:
            if pores == 'all':
                pores = self.get_pore_indices(labels='all')
            return self._get_data(element='pore',prop=prop,locations=pores,mode=mode)
        if throats != []:
            if throats == 'all':
                throats = self.get_throat_indices(labels='all')
            return self._get_data(element='throat',prop=prop,locations=throats,mode=mode)
            
    def set_data(self,prop='',data='',pores=[],throats=[],mode='merge'):
        r'''
        Write data according to input arguments.
        
        Parameters
        ----------
        prop : string
            Name of property to retrieve.
        pores : array_like, or string 'all'
            List of pore indices to which data will be written.
        throats : array_like, or string 'all'
            List of throat indices to which data will be written.
            
        See Also
        --------
        set_info
        
        Notes
        -----
        This is a wrapper method that calls _set_data.  
        Only one of pores or throats should be sent.
            
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> pn.set_data(prop='test',pores=[0],data=1.1)
        >>> pn.get_data(prop='test',pores=[0])
        array([ 1.1])
        '''
        data= sp.array(data,ndmin=1)
        if pores != []:
            if pores == 'all':
                if sp.shape(data)[0] == 1:
                    pores = ''
                else:
                    pores = self.get_pore_indices(labels='all')
            self._set_data(element='pore',prop=prop,data=data,locations=pores,mode=mode)
        if throats != []:
            if throats == 'all':
                if sp.shape(data)[0] == 1:
                    throats = ''
                else:
                    throats = self.get_throat_indices(labels='all')
            self._set_data(element='throat',prop=prop,data=data,locations=throats,mode=mode)    

    def set_pore_data(self,prop='',data='',locations='',mode='merge'):
        r'''
        THIS METHOD IS DEPRECATED, USE set_data INSTEAD
        '''
        self._set_data(element='pore',prop=prop,data=data,locations=locations,mode=mode)
        
    def get_pore_data(self,prop='',locations=''):
        r'''
        THIS METHOD IS DEPRECATED, USE get_data INSTEAD
        '''
        return self._get_data(element='pore',prop=prop,locations=locations)

    def set_throat_data(self,prop='',data='',locations='',mode='merge'):
        r'''
        THIS METHOD IS DEPRECATED, USE set_data INSTEAD        
        '''
        self._set_data(element='throat',prop=prop,data=data,locations=locations,mode=mode)         

    def get_throat_data(self,prop='',locations=''):
        r'''
        THIS METHOD IS DEPRECATED, USE get_data INSTEAD
        '''
        return self._get_data(element='throat',prop=prop,locations=locations)     

    def _set_info(self,element='',label='',locations='',mode='merge'):
        r'''
        This is the actual info setter method, but it should not be called directly.  
        Wrapper methods have been created.  Use set_info().
        '''
        if type(locations)==list: 
            try: locations = getattr(self,'get_'+element+'_indices')(locations)
            except: locations = sp.array(locations,ndmin=1)
        elif type(locations)==sp.ndarray:
            try: locations = getattr(self,'get_'+element+'_indices')(locations)
            except : pass 
        if locations!='':
            
            try: 
                locations = locations.name
                label = locations
            except: pass
            if type(locations)==str: locations = getattr(self,'get_'+element+'_indices')([locations])           
            locations=sp.array(locations,ndmin=1)
            if label:
                if label=='all':
                    try: 
                        old_label = getattr(self,'_'+element+'_info')[label]
                        if sp.shape(old_label)[0]<sp.shape(locations)[0]:
                            getattr(self,'_'+element+'_info')[label] = sp.ones_like(locations,dtype=bool)
                            self._logger.info('label=all for '+element+'has been updated to a bigger size!')
                            for info_labels in getattr(self,'_'+element+'_info').keys():
                                if info_labels!=label:
                                    temp = sp.zeros((getattr(self,'num_'+element+'s')(),),dtype=bool)
                                    temp[old_label] = getattr(self,'_'+element+'_info')[info_labels]
                                    getattr(self,'_'+element+'_info')[info_labels] = temp
                        elif sp.shape(old_label)[0]>sp.shape(locations)[0]: 
                            self._logger.error('To apply a new numbering label (label=all) to '+element+'s, size of the locations cannot be less than total number of '+element+'s!!')
                    except: getattr(self,'_'+element+'_info')[label] = sp.ones_like(locations,dtype=bool)
                else:    
                    try: getattr(self,'_'+element+'_info')[label]
                    except: getattr(self,'_'+element+'_info')[label] = sp.zeros((getattr(self,'num_'+element+'s')(),),dtype=bool)
                    if mode=='overwrite':
                        getattr(self,'_'+element+'_info')[label] = sp.zeros((getattr(self,'num_'+element+'s')(),),dtype=bool)
                        getattr(self,'_'+element+'_info')[label][locations] = True
                    elif mode=='remove':  getattr(self,'_'+element+'_info')[label][locations] = False                           
                    elif mode=='merge':  getattr(self,'_'+element+'_info')[label][locations] = True
            else: self._logger.error('No label has been defined for these locations')                

        elif mode=='remove':  del getattr(self,'_'+element+'_info')[label]
        else:  getattr(self,'_'+element+'_info')[label] = sp.zeros((getattr(self,'num_'+element+'s')(),),dtype=bool)

    def _get_info(self,element='',label='',return_indices=False,mode=''):
        r'''
        This is the actual info getter method, but it should not be called directly.  
        Wrapper methods have been created.  Use get_info().        
        '''
        if return_indices:
            return sp.where(getattr(self,'_'+element+'_info')[label]==True)[0]
        else:
            return getattr(self,'_'+element+'_info')[label]
            
    def set_info(self,label='',pores=[],throats=[],mode='merge'):
        r'''
        Apply a label to a selection of pores or throats
        
        Parameters
        ----------
        label : string
            The name of the pore labels you wish to apply (e.g. 'top')
        pores or throats : array_like
            An array containing the pore (or throat) indices where the labels 
            should be applied.  Can be either a boolean mask of Np length with 
            True at labels locations (default), a list of indices where labels 
            should be applied.
        mode : string
            Set the mode to be used for writing labels.  Options are:
            
            * 'merge' : (default) Adds label to specified locations while 
            maintaining pre-existing labels
            
            * 'overwrite' : Adds label to specified locations while 
            removing all pre-existing labels
            
            * 'remove' : Removes labels from specified locations.  If no
            locations are given then this mode will remove the entire label
            from the network.
        '''
        if pores != []:
            if pores == 'all':
                pores = self.pores(labels='all')
            self._set_info(element='pore',label=label,locations=pores,mode=mode)
        if throats != []:
            if throats == 'all':
                throats = self.get_throat_indices(labels='all')
            self._set_info(element='throat',label=label,locations=throats,mode=mode)
            
    def get_info(self,label='',pores=[],throats=[],return_indices=True):
        r'''
        Retrieves the locations where the specified label is applied
        
        Parameters
        ----------
        label : string
            Label of interest
        pores (or throats) : array_like
            List of pores or throats
        return_indices : boolean
            Controls whether a list of indices (default) or a boolean mask is
            returned
            
        See Also
        --------
        get_labels
            
        '''
        if pores != []:
            if pores == 'all':
                pores = self.pores(labels='all')
            temp = self._get_info(element='pore',label=label,return_indices=return_indices)
            if return_indices == False:
                return temp[pores]
            else:
                return temp[sp.in1d(temp,pores)]
        if throats != []:
            if throats == 'all':
                throats = self.throats(labels='all')
            temp = self._get_info(element='throat',label=label,return_indices=return_indices)
            if return_indices == False:
                return temp[throats]
            else:
                return temp[sp.in1d(temp,throats)]
           
    def set_pore_info(self,label='',locations='',mode='merge'):
        r'''
        THIS METHOD IS DEPRECATED, USE set_info INSTEAD
        '''
        self._set_info(element='pore',label=label,locations=locations,mode=mode)

    def get_pore_info(self,label='',return_indices=False):
        r'''
        THIS METHOD IS DEPRECATED, USE get_info INSTEAD
        '''
        return self._get_info(element='pore',label=label,return_indices=return_indices)
        
    def set_throat_info(self,label='',locations='',mode='merge'):
        r'''
        THIS METHOD IS DEPRECATED, USE set_info INSTEAD
        '''
        self._set_info(element='throat',label=label,locations=locations,mode=mode)
        
    def get_throat_info(self,label='',return_indices=False):
        r'''
        THIS METHOD IS DEPRECATED, USE get_info INSTEAD
        '''
        return self._get_info(element='throat',label=label,return_indices=return_indices)
        
    def list_pore_props(self):
        r'''
        Returns a list containing the names of all defined pore properties.
        This list is an iterable, so is useful for scanning through labels.

        Returns
        -------
        A an alphabetically sorted list containing the string name of all 
        pore properties currently defined.  

        See Also
        --------
        list_throat_props, list_pore_labels, list_throat_labels
        '''
        temp = list(self._pore_data.keys())
        temp.sort()
        return temp

    def list_throat_props(self):
        r'''
        Returns a list containing the names of all defined throat properties. 
        This list is an iterable, so is useful for scanning through labels.

        Returns
        -------
        A an alphabetically sorted list containing the string name of all 
        throat properties currently defined.  

        See Also
        --------
        list_pore_props, list_pore_labels, list_throat_labels
        '''
        temp = list(self._throat_data.keys())
        temp.sort()
        return temp
        
    def list_pore_labels(self):
        r'''
        Returns a list containing the names of all defined pore labels. This
        list is an iterable, so is useful for scanning through labels.

        Returns
        -------
        A an alphabetically sorted list containing the string name of all 
        pore labels currently defined.  

        See Also
        --------
        list_throat_props, list_pore_props, list_throat_labels
        '''
        temp = list(self._pore_info.keys())
        temp.sort()
        return sp.array(temp,ndmin=1)

    def list_throat_labels(self):
        r'''
        Returns a list containing the names of all defined throat labels. This
        list is an iterable, so is useful for scanning through labels.
        
        Returns
        -------
        A an alphabetically sorted list containing the string name of all 
        throat labels currently defined.  
        
        See Also
        --------
        list_throat_props, list_pore_props, list_pore_labels
        '''
        temp = list(self._throat_info.keys())
        temp.sort()
        return sp.array(temp,ndmin=1)
        
    def _get_labels(self,element,locations,mode='union',flatten=False):
        r'''
        This is the actual label getter method, but it should not be called directly.  
        Wrapper methods have been created.  Use get_labels().
        '''
        if element == 'pore':
            element_info = self._pore_info
            labels = self.list_pore_labels()
        elif element == 'throat':
            element_info = self._throat_info
            labels = self.list_throat_labels()
        arr = sp.ndarray((sp.shape(locations,)[0],len(labels)),dtype=bool)
        col = 0
        for item in labels:
            arr[:,col] = element_info[item][locations]
            col = col + 1
        if flatten == True:
            if mode == 'count':
                return sp.sum(arr,axis=1)
            if mode == 'union':
                return labels[sp.sum(arr,axis=0)>0]
            if mode == 'intersection':
                return labels[sp.sum(arr,axis=0)==sp.shape(locations,)[0]]
        else:
            if mode == 'raw':
                return arr
            else:
                temp = sp.ndarray((sp.shape(locations,)[0],),dtype=object)
                for i in sp.arange(0,sp.shape(locations,)[0]):
                    temp[i] = list(labels[arr[i,:]])
                return temp
                
    def get_labels(self,pores=[],throats=[],mode='union',flatten=False):
        r'''
        Returns the labels applied to specified pore locations
        
        Parameters
        ----------
        pores (or throats) : array_like
            The pores (or throats) whos labels are sought
        flatten : boolean, optional
            If False (default) the returned list is Np (or Nt) long, where each
            element is a list labels applied to the specified pores.  If True, 
            the mode logic
        mode : string, optional
            Controls how the query should be performed
            
            * 'union' : A list of labels applied to ANY of the given locations
            
            * 'intersection' : Label applied to ALL of the given locations
            
            * 'count' : The number of labels on each pore
            
            * 'raw' : returns an Np x Nlabels array, where each row corresponds
            to a pore location, and each column contains the truth value for
            the existance of labels as returned from list_pore_labels().
            
        Notes
        -----
        The mode argument is ignored unless flatten is True, with the exception 
        of 'raw'.
        '''
        if pores != []:
            pores = sp.array(pores,ndmin=1)
            return self._get_labels(element='pore',locations=pores, mode=mode, flatten=flatten)
        if throats != []:
            throats = sp.array(throats,ndmin=1)
            return self._get_labels(element='throat',locations=throats,mode=mode,flatten=flatten)

    def get_pore_labels(self,pnums,mode='union',flatten=False):
        r'''
        THIS METHOD IS DEPRECATED, SEE get_labels()
        '''
        pnums = sp.array(pnums,ndmin=1)
        temp = self._get_labels(element='pore',locations=pnums, mode=mode, flatten=flatten)
        return temp

    def get_throat_labels(self,tnums,mode='union',flatten=False):
        r'''
        THIS METHOD IS DEPRECATED, SEE get_labels()
        '''
        tnums = sp.array(tnums,ndmin=1)
        temp = self._get_labels(element='throat',locations=tnums,mode=mode,flatten=flatten)
        return temp
        
    def _get_indices(self,element,labels,return_indices,mode):
        r'''
        This is the actual method for getting indices, but should not be called
        directly.  
        '''
        try: labels = [labels.name]  # Check if object was sent
        except: pass
        if mode == 'union':
            union = sp.zeros_like(self._get_info(element=element,label='all'),dtype=bool)
            for item in labels: #iterate over labels list and collect all indices
                    union = union + self._get_info(element=element,label=item)
            ind = union
        elif mode == 'intersection':
            intersect = sp.ones_like(self._get_info(element=element,label='all'),dtype=bool)
            for item in labels: #iterate over labels list and collect all indices
                    intersect = intersect*self._get_info(element=element,label=item)
            ind = intersect
        elif mode == 'not_intersection':
            not_intersect = sp.zeros_like(self._get_info(element=element,label='all'),dtype=int)
            for item in labels: #iterate over labels list and collect all indices
                info = self._get_info(element=element,label=item)
                not_intersect = not_intersect + sp.int8(info)
            ind = (not_intersect == 1)
        elif mode == 'none':
            none = sp.zeros_like(self._get_info(element=element,label='all'),dtype=int)
            for item in labels: #iterate over labels list and collect all indices
                info = self._get_info(element=element,label=item)
                none = none - sp.int8(info)
            ind = (none == 0)
        if return_indices: ind = sp.where(ind==True)[0]
        return ind

    def get_pore_indices(self,labels=['all'],return_indices=True,mode='union'):
        r'''
        THIS METHOD IS DEPRECATED, USE pores() INSTEAD
        '''
        return self.pores(labels=labels,return_indices=return_indices,mode=mode)

    def get_throat_indices(self,labels=['all'],return_indices=True,mode='union'):
        r'''
        THIS METHOD IS DEPRECATED, USE throats() INSTEAD
        '''
        return self.throats(labels=labels,return_indices=return_indices,mode=mode)
        
    def pores(self,labels='all',return_indices=True,mode='union'):
        r'''
        Returns pore locations where given labels exist.
        
        Parameters
        ----------
        labels : list of strings, optional
            The pore label(s) whose locations are requested.
            If omitted, all pore inidices are returned.
        indices : boolean, optional
            This flag specifies whether pore locations are returned a boolean mask of length Np,
            or as a list of indices (default).
        mode : string, optional
            Specifies how the query should be performed.  The options are:    

            * 'union' : (default) All pores with ANY of the given labels are 
            returned.

            * 'intersection' : Only pore with ALL the given labels are 
            returned.

            * 'not_intersection' : Only pores with exactly one of the given 
            labels are returned.
            
            * 'none' : Only pores with none of the given labels are returned.
        
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> pind = pn.get_pore_indices(labels=['top','front'],mode='union')
        >>> pind[[0,1,2,-3,-2,-1]]
        array([  0,   5,  10, 122, 123, 124], dtype=int64)
        >>> pn.get_pore_indices(labels=['top','front'],mode='intersection')
        array([100, 105, 110, 115, 120], dtype=int64)
        '''
        if type(labels) == str: labels = [labels] #convert string to list, if necessary
        ind = self._get_indices(element='pore',labels=labels,return_indices=return_indices,mode=mode)
        return ind
        
    def throats(self,labels='all',return_indices=True,mode='union'):
        r'''
        Returns throat locations where given labels exist.
        
        Parameters
        ----------
        labels : list of strings, optional
            The throat label(s) whose locations are requested.
            If omitted, 'all' throat inidices are returned.
        return_indices : boolean, optional
            This flag specifies whether throat locations are returned as a 
            boolean mask of length Np, or as a list of indices (default).
        mode : string, optional
            Specifies how the query should be performed.  The options are: 

            * 'union' : (default) All throats with ANY of the given labels are 
            returned.

            * 'intersection' : Only throats with ALL the given labels are 
            counted.

            * 'not_intersection' : Only throats with exactly one of the given 
            labels are counted.
            
            * 'none' : Only throats with none of the given labels are returned.
        
        Notes
        -----
        This method replaces get_throat_indices
        
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> Tind = pn.get_throat_indices()
        >>> Tind[0:5]
        array([0, 1, 2, 3, 4], dtype=int64)
        
        '''
        if type(labels) == str: labels = [labels] #convert string to list, if necessary
        ind = self._get_indices(element='throat',labels=labels,return_indices=return_indices,mode=mode)
        return ind

    def interpolate_data(self,prop='',throats=[],pores=[],data=[]):
        r"""
        Determines a pore (or throat) property as the average of it's neighboring 
        throats (or pores)

        Parameters
        ----------
        pores : array_like
            The pores for which values are desired
        throats : array_like
            The throats for which values are desired
        data : array_like
            A list of specific values to be interploated.  List MUST be either
            Np or Nt long
        
        Returns
        -------
        values : array_like
            An array containing interpolated pore (or throat) data

        Notes
        -----
        - This uses an unweighted average, without attempting to account for 
        distances or sizes of pores and throats.
        - Only on of pores, throats OR data are accepted
        
        Examples
        --------
        

        """
        if self.__module__.split('.')[1] == 'Network': net = self
        else: net = self._net
        if sp.shape(data)[0] > 0:
            prop='tmp'
            values = sp.array(data,ndmin=1)
            if sp.shape(values)[0] == net.num_pores():
                throats = net.get_throat_indices('all')
                self.set_data(prop=prop,pores='all',data=values)
            elif sp.shape(values)[0] == net.num_throats():
                pores = self.get_pore_indices('all')
                self.set_data(prop=prop,throats='all',data=values)
            elif sp.shape(values)[0] == 1: #if scalar was sent
                return values
            else:
                self._logger.error('Received data of an ambiguous length')
                return
        if sp.shape(pores)[0] > 0:
            throats = net.find_neighbor_throats(pores,flatten=False)
            throat_data = self.get_data(prop=prop,throats='all')
            values = sp.ones((sp.shape(pores)[0],))*sp.nan
            if sp.shape(throat_data)[0] == 1:
                values = throat_data
            else:
                for i in pores:
                    values[i] = sp.mean(throat_data[throats[i]])
        elif sp.shape(throats)[0] > 0:
            pores = net.find_connected_pores(throats,flatten=False)
            pore_data = self.get_data(prop=prop,pores='all')
            values = sp.ones((sp.shape(throats)[0],))*sp.nan
            if sp.shape(pore_data)[0] == 1:
                values = pore_data
            else:
                values = sp.mean(pore_data[pores],axis=1)
        return values
        
    def num_pores(self,labels=['all'],mode='union'):
        r'''
        Returns the number of pores of the specified labels

        Parameters
        ----------
        labels : list of strings, optional
            The pore labels that should be included in the count.  
            If not supplied, all pores are counted.
        labels : list of strings
            Label of pores to be returned
        mode : string, optional
            Specifies how the count should be performed.  The options are: 
            
            * 'union' : (default) All pores with ANY of the given labels are counted.

            * 'intersection' : Only pores with ALL the given labels are counted.
            
            * 'not_intersection' : Only pores with exactly one of the given labels are counted.
            
            * 'none' : Only pores with none of the given labels are counted.
            
        Returns
        -------
        Np : int
            Number of pores with the specified labels 
            
        See Also
        --------
        num_throats
            
        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> pn.num_pores()
        125
        >>> pn.num_pores(labels=['top'])
        25
        >>> pn.num_pores(labels=['top','front'],mode='union') #'union' is default
        45
        >>> pn.num_pores(labels=['top','front'],mode='intersection')
        5
        >>> pn.num_pores(labels=['top','front'],mode='not_intersection')
        40
        
        '''
        #convert string to list, if necessary
        if type(labels) == str: labels = [labels]
        #Count number of pores of specified type
        temp = self.get_pore_indices(labels=labels,mode=mode,return_indices=False)
        return sp.sum(temp) #return sum of Trues
            
    def num_throats(self,labels=['all'],mode='union'):
        r'''
        Return the number of throats of the specified labels

        Parameters
        ----------
        labels : list of strings, optional
            The throat labels that should be included in the count.  
            If not supplied, all throats are counted.
        mode : string, optional
            Specifies how the count should be performed.  The options are: 

            * 'union' : (default) All throats with ANY of the given labels are counted.

            * 'intersection' : Only throats with ALL the given labels are counted.

            * 'not_intersection' : Only throats with exactly one of the given labels are counted.
            
            * 'none' : Only throats with none of the given labels are counted.

        Returns
        -------
        Nt : int
            Number of throats with the specified labels
            
        See Also
        --------
        num_pores

        Examples
        --------
        >>> pn = OpenPNM.Network.TestNet()
        >>> pn.num_throats()
        300
        >>> pn.num_throats(labels=['top'])
        40
        >>> pn.num_throats(labels=['top','front'],mode='union') #'union' is default
        76
        >>> pn.num_throats(labels=['top','front'],mode='intersection')
        4
        >>> pn.num_throats(labels=['top','front'],mode='not_intersection')
        72
        
        '''
        #convert string to list, if necessary
        if type(labels) == str: labels = [labels]
        #Count number of pores of specified type
        temp = self.get_throat_indices(labels=labels,mode=mode,return_indices=False)
        return sp.sum(temp) #return sum of Trues
        
    def get_result(self,alg_obj,**kwargs):
        r'''
        This method invokes the update method on the given OpenPNM Algorithm object
        
        Parameters
        ----------
        alg_obj : OpenPNM Algorithm object
        
        Notes
        -----
        For specific details refer to the `update` of the algorithm.
        '''
        alg_obj.update(**kwargs)

    def _check_health(self,element='',props=[]):
        r'''
        '''
        success = 1
        if type(props)==str: 
            props = [props]
        if props != []:
            items = props
        else: 
            items = getattr(self,'_'+element+'_data').keys()
        for item in items:
            try: 
                temp = getattr(self,'_'+element+'_data')[item]
                if sp.sum(sp.isnan(temp)) > 0:
                    self._logger.warning('Nans found in: '+item)
                    success = 0
                else: self._logger.info('Checks for property: '+item+', passed successfully.')
            except:
                self._logger.error('Property: '+item+' not found!')
                success = 0
        if success == 1:
            self._logger.info('All checks passed successfully.')
        return success
        
    def check_pore_health(self,props=[]):
        r'''
        '''
        self._check_health(element='pore',props=props)
        
    def check_throat_health(self,props=[]):
        r'''
        '''
        self._check_health(element='throat',props=props)
        

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

