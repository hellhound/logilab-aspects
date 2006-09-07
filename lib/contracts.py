# -*- coding: ISO-8859-1 -*-
# pylint: disable-msg=W0142
# Copyright (c) 2003-2006 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# forall() and exists() are taken from 'pycontract'
# written by Terence Way (terry@wayforward.net)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
Contracts module
Allow the use of contracts in code
Implemented :
   - pre conditions
   - post conditions
   - invariants
   - value holders to memorize values before procedure execution
   - Inheritance management :
       * pre conditions are ORed => allow to keep or weaken base pre-cond
       * post conditions are ANDed => allow to keep or strengthen base post-cond
       * inv conditions are ANDed

Still to do:
   - (??) rescue clause ?



forall() and exists() are taken from 'pycontract'
written by Terence Way (terry@wayforward.net)

"""

__revision__ = '$Id: contracts.py,v 1.27 2005-12-30 16:29:07 adim Exp $'

from logilab.aspects.core import AbstractAspect
from logilab.aspects._exceptions import AspectFailure
from logilab.aspects.prototypes import reassign_function_arguments
from logilab.aspects.weaver import weaver

import re
import types

OLD_PATTERN = '__old__\.(([^ \t$\(\[\)\]]+)([\(\[].*[\)\]])*)'
# OLD_PATTERN = '__old__\[[\'"](.*?)[\'"]\]'
OLD_PROG = re.compile(OLD_PATTERN)

# Utilities fuctions ###########################################################
def parse_docstring(doc_str) :
    """
    can read
    '''this is a docstring with a contract

    pre:
        # comments are allowed in contracts
        # it's advised to indent the blocks, though it is not required
        # in the current version. 
        a>1
        b<5
    post:
        r>2
    inv:
        self.i == 0
    '''
    and return
    pre = ['a>1','b<5']
    post = ['r>2']
    inv = ['self.i == 0']
    """

    condition_delim = "---"
    pre = []
    post = []
    inv = []
    if not doc_str:
        return pre, post, inv

    state = None 
    for line in doc_str.split('\n') :
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        elif line.startswith('pre:') :
            state = 'pre'
        elif line.startswith('post:') :
            state = 'post'
        elif line.startswith('inv:') :
            state = 'inv'
        elif line.startswith(condition_delim):
            state = None
        elif state == 'pre' :
            pre.append(line)
        elif state == 'post' :
            post.append(line)
        elif state == 'inv' :
            inv.append(line)

    return pre, post, inv




def _remove_doubles(lst):
    """Remove doubles from lst and returns the computed list
    """
    # is it really faster (than defining a list) like this ?
    defined_items = {}
    clean_list = []
    for item in lst:
        if item not in defined_items:
            clean_list.append(item)
            # set an arbitrary value, just create the item's key
            defined_items[item] = ""

    return clean_list

def get_base_classes(klass):
    """Returns the bases clases (recursively) of klass
    Prefix algorithm.
    The returned list does not contain any doubles
    """

    base_classes = []
    for base in klass.__bases__:
        base_classes.append(base)
        base_classes += get_base_classes(base)

    return base_classes


def simple_mro(klass):
    """Defines a very simple Method Resolution Order for contracts
    /!\ this mro does **not** include original class ! (well, it's
        not really a mro then, but)
    """
    bases = get_base_classes(klass)
    return _remove_doubles(bases)


def get_ancestors_conditions(cls, method_name):
    """ Returns all ancestors' precondtions in a list
    of lists : [[cond1_base1,cond2_base1], [cond1_base2]]
    cls : the class
    method_name : name of the method to process
    """

    if type(cls) == types.ClassType:
        klass = cls
    else:
        klass = cls.__class__

    current_module = cls.__module__
    pre, post, inv = [], [], []
    # First, get the invariant conditions of the module
    inv.append(parse_docstring(current_module.__doc__)[2])
    # we don't want to parse the same module several times
    processed_modules = [current_module]
    # for each base_class, try to get pre/post/inv conditions
    for base_class in simple_mro(klass):
        # Add module invariants if it's not already done
        if base_class.__module__ not in processed_modules:
            current_module = base_class.__module__
            module_inv = parse_docstring(current_module.__doc__)[2]
            inv.append(module_inv)
            processed_modules.append(current_module)
        # Add the class invariants
        class_inv = parse_docstring(base_class.__doc__)[2]
        # Add the method invariants
        inv.append(class_inv)
        # Checks if method exists in base_class
        if method_name in base_class.__dict__:
            doc_str = getattr(base_class, method_name).__doc__
            base_pre, base_post, base_inv = parse_docstring(doc_str)
            # Add all condtions (no check for duplicatde conditions)
            pre.append(base_pre)
            post.append(base_post)
            inv.append(base_inv)

    return pre, post, inv


class ContractFailedError(AspectFailure):
    """raised when a contract failed"""
    pass


# Contract Functions ##########################################################

def forall(lst, mapped_func = bool):
    """Checks that all elements in a sequence are true.
    lst : the sequence
    mapped_func : the func applied to all elements of the sequence

    Returns True(1) if all elements are true.  Return False(0) otherwise.

    >>> forall([True, True, True])
    1
    >>> forall( () )
    1
    >>> forall([True, True, False, True])
    0
    """
    for item in lst:
        if not mapped_func(item):
            return False
    return True


def exists(lst, mapped_func = bool):
    """Checks that at least one element in a sequence is true
    lst : the sequence
    mapped_func : the func applied to all elements of the sequence

    Returns True(1) if at least one element is true.  Return False(0)
    otherwise.

    >>> exists([False, False, True])
    1
    >>> exists([])
    0
    >>> exists([False, 0, '', []])
    0
    """
    for item in lst:
        if mapped_func(item):
            return True
    return False



# The Contract Aspect ##########################################################
class ContractAspect(AbstractAspect):
    """Implementation of contracts using aspects.
    """

    def __init__(self, pointcut):
        # contract_definitions has the same key / value behaviour that
        # self._methods (self <=> aspect instance)
        self._contract_definitions = {}

        AbstractAspect.__init__(self, pointcut)



    def _update_methods(self, pointcut):
        """Override AbstractAspect's update_methods because we also need
        to update self._contract_definitions, and loops are exactly the
        same for both self._methods andself._contract_definitions (i.e.
        it's just a performance optimization. (We might fix this with
        an appropriate hook)
        """
        for weaved_object, method_names in pointcut.items():
            method_map = self._methods.get(weaved_object, {})
            contract_map = {} # self._contract_definitions[weaved_object]
            
            for met_name in method_names:
                base_method, method = weaver.get_original_method(weaved_object,
                                                                 met_name)
                # if met_name not in method_map:
                method_map[met_name] = (method, base_method)
                # if met_name not in contract_map:
                contract_map[met_name] = self.precompile_contracts(
                    weaved_object, base_method)
            
            self._methods[weaved_object] = method_map
            self._contract_definitions[weaved_object] = contract_map
        


    def precompile_contracts(self, obj, method):
        """Returns a tuple with four elements :
            - the precompiled preconditions
            - the precompiled postconditions
            - the precompiled invariants
            - the holder that stores variable states for post conditions
        """
        m_pre, m_post, m_inv = parse_docstring(method.__doc__)
        
        module_inv = parse_docstring(obj.__module__.__doc__)[2]
        class_inv = parse_docstring(obj.__doc__)[2]        
        
        # pre/post/inv are lists where each element is the list of
        # pre/post/inv conditions of each class in the inheritance tree
        pre, post = [m_pre], [m_post]
        inv =  [module_inv + class_inv + m_inv]
        base_pre, base_post, base_inv = \
                  get_ancestors_conditions(obj, method.__name__)
        # PRE-conditions inherited can only be kept or weaken. If a new
        # set of pre-conditions exists, then it overrides the base ones, else
        # we must take the base ones.
        pre += base_pre
        # POST-conditions inherited can only be kept or strengthen. To
        # achieve this, we concatenante new post conditions (if there are)
        # to base ones.
        post += base_post
        inv  += base_inv
        
        holder = dict([(varname, None)
                       for varname in self._get_variables_to_memorize(post)])
        
        pre = [cond_list for cond_list in pre if len(cond_list)]
        post = [cond_list for cond_list in post if len(cond_list)]
        inv = [cond_list for cond_list in inv if len(cond_list)]

        compiled_pre = self._compile_conditions(pre, ' or ')
        compiled_post = self._compile_conditions(post, ' and ')
        compiled_inv = self._compile_conditions(inv, ' and ')

        # XXX FIXME : returning holder is not a good way to proceed !!
        return compiled_pre, compiled_post, compiled_inv, holder
    
    
    def _get_definitions(self, wobj, met_name):
        """Will try to find the appropriate contract definitions object according
        to wobj and met_name.
        Raises a KeyError if method cannot be found.
        """
        try:
            return self._contract_definitions[wobj][met_name]
        except KeyError:
            return self._contract_definitions[wobj.__class__][met_name]
    

    def _get_variables_to_memorize(self, post_conditions):
        """Initializes variables that need to be memorized
        and return them in a list
        """
        memo_list = []
        for cond_list in post_conditions:
            # the regexp substitution is needed for backward compatibility
            index = 0
            for cond in cond_list[:]:
                # get all __old__ vars
                groups = OLD_PROG.findall(cond)
                # XXX FIXME : should this be done in parse_docstring() ?
                for group in groups:
                    memo_list.append(group[0])
                cond_list[index] = OLD_PROG.sub(r"__old__['\1']", cond)
                index += 1
        return memo_list
    

    def _compile_conditions(self, cond_set, join_type):
        """ pre-compile conditions
        cond_set : a list of cond_list (self.pre/post/inv)
        join_type : a string representing the operator to
        use depending on the fact conditions can be weaken or strentghned
        """
        source_code = []
        for cond_list in cond_set:
            embraced_conditions = ['('+cond+')' for cond in cond_list]
            source_code.append(" and ".join(embraced_conditions))

        # if there are some conditions
        if len(source_code):
            return compile(join_type.join(source_code), "contracts.py", "eval")
        else:
            return None



    def _check_conditions(self, conditions_code, local_dict, cond_type):
        """Checks conditions.
        conditions_code : the compiled conditions (computed by
        _compile_conditions)
        local_dict : the dictionnary of existing variables when contracted
        method call was done.
        cond_type : a string in ('pre', 'post', 'inv')
        """
        try:
            assert eval(conditions_code, local_dict)
        except AssertionError, excpt:
            raise ContractFailedError("%s-conditions not satisfied : %s"%
                                      (cond_type, excpt))

        
        
    def before(self, wobj, context, *args, **kwargs):
        """
        self : aspect instance
        wobj : the weaved object instance
        global_dict : the wrapped_func globals dict (f.func_globals)
        """
        met_name = context['method_name']
        base_method = self._get_base_method(wobj, met_name)
        local_dict = {}
        method_dict = base_method.im_func.func_globals
        local_dict.update(method_dict)
        pre, dummy, inv, holder = self._get_definitions(wobj, met_name)
        
        local_dict.update(reassign_function_arguments(base_method,
                                                      args, kwargs))
        local_dict['self'] = wobj
        local_dict['exists'] = exists
        local_dict['forall'] = forall
        
        # Memorize state of variables which are needed with __old__ in post
        # conditions.
        # for var in holder.memo_list:
        #     holder.set(var, eval(var, local_dict))
        for var in holder.iterkeys():
            holder[var] = eval(var, local_dict)
        
        # First check invariants
        ##########################################################
        # We use __aspecting_inv__ a bit as a lock() to prevent
        # infinite loops if method calls are done on self in
        # invariant conditions
        ##########################################################
        
        # Skip invariant checks if we're already in one of those
        if '__aspecting_inv__' not in wobj.__dict__:
            wobj.__dict__['__aspecting_inv__'] = True
            if inv is not None:
                self._check_conditions(inv, local_dict, "inv")
            # self._check_invariants(wobj, local_dict)
            del wobj.__dict__['__aspecting_inv__']
            
        # Then check pre-conditions
        # self._check_pre_conditions(wobj, local_dict)
        if pre is not None:
            self._check_conditions(pre, local_dict, "pre")
        
        
    def after(self, wobj, context, *args, **kwargs):
        """
        self    : aspect instance
        wobj    : the weaved object instance
        global_dict : the wrapped_func globals dict (f.func_globals)
        ret_v   : the return value of the wrapped method
        exec_excpt : the exception raised by the wrapped method or None
        if no exception has been raised
        """
        met_name = context['method_name']
        ret_v = context['ret_v']
        exec_excpt = context['exception']
        
        base_method = self._get_base_method(wobj, met_name)
        local_dict = {}
        method_dict = base_method.im_func.func_globals
        local_dict.update(method_dict)

        dummy, post, inv, holder = self._get_definitions(wobj, met_name)

        local_dict.update(reassign_function_arguments(
            base_method, args, kwargs))
        local_dict['self'] = wobj
        local_dict['__return__'] = ret_v
        local_dict['__old__'] = holder
        local_dict['exists'] = exists
        local_dict['forall'] = forall

        # First check invariants
        ##########################################################
        # We use __aspecting_inv__ a bit as a lock() to prevent
        # infinite loops if method calls are done on self in
        # invariant conditions
        ##########################################################
        
        # Skip invariant checks if we're already in one of those
        if '__aspecting_inv__' not in wobj.__dict__:
            wobj.__dict__['__aspecting_inv__'] = True
            # self._check_invariants(wobj, local_dict)
            if inv is not None:
                self._check_conditions(inv, local_dict, "inv")
            del wobj.__dict__['__aspecting_inv__']

        # Check post-conditions if no exception has been raised
        if exec_excpt is None:
            # self._check_post_conditions(wobj, local_dict)
            if post is not None:
                self._check_conditions(post, local_dict, "post")



def enable_dbc_on(obj):
    weaver.weave_object(obj, ContractAspect)
