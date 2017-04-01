import settings
import os
import sys
import pickle

class DataView:
  
  def __init__(self, symbol, date, ftype, start_path=''):
    #adding this start path bit to load DataViewer from other dirs, it's just the path to the ScraXBRL
    self.start_path = start_path
    self.symbol = symbol
    self.date = date
    self.ftype = ftype
    self.data = None
    self.load_data()
    self.path_pairs = []
  
  def load_data(self):
    fpath_no_p = self.start_path + "{0}/{1}/{2}/xml/{3}/".format(settings.EXTRACTED_DATA_PATH,
                 self.symbol,
                 self.ftype,
                 self.date)
    fpath_file = os.listdir(fpath_no_p)[0]
    fpath = "{0}/{1}".format(fpath_no_p, fpath_file)
    self.data = pickle.load(open(fpath, 'rb'))
  
  def get_all_roles(self, cat='pre'):
    """Returns list of all roles."""
    
    return self.data[cat]['roles'].keys()
  
  def traverse_print_tree(self, base, role_keys, tabs=0):
    """Traverse cal tree and print."""

    for rk in role_keys:
      if rk == 'sub':
        continue
      tab_str = '   ' * tabs
      try:
        lab_str = tab_str + str(rk)
      except KeyError:
        lab_str = rk
      try:
        base_keys = base[rk]['val'].keys()
        if len(base_keys) == 0:
          if len(base[rk]['sub']) == 0:
            continue
          else:
            print('\033[1m' + lab_str + '\033[0m')
        else:
          date_str = ''
          val_str = ''
          for i in base_keys:
            date_str += str(i)
            date_str += '\t\t'
          for bk in base_keys:
            if base[rk]['val'][bk] == None:
              continue
            if isinstance(base[rk]['val'][bk], float):
              val_str += str(base[rk]['val'][bk])
            else:
              val_str += base[rk]['val'][bk].encode('utf-8')
            val_str += '\t\t'
          print(lab_str)
          print(tab_str + '\t' + date_str)
          print(tab_str + '\t' + val_str)
      except KeyError:
        pass
      if len(base[rk]['sub']) > 0:
        rk_base = base[rk]['sub']
        rk_base_keys = rk_base.keys()
        self.traverse_print_tree(rk_base, rk_base_keys, tabs=tabs+1)
        
  def traverse_tree(self, name, cat='pre'):
    base = self.data[cat]['roles'][name]
    base_tree = base['tree']
    role_keys = base_tree.keys()
    self.traverse_print_tree(base_tree, role_keys)
  
  def traverse_all_trees(self):
    base = self.data['pre']['roles']
    base_keys = base.keys()
    for bk in base_keys:
      print('\033[1m' + 'Title:' + ' ' + bk + '\033[0m')
      self.traverse_tree(bk)
      print('\n\n')
        
  def find_fact_in_role(self, fact, cat='pre'):
    """Returns list of roles with fact in them."""
    
    all_role_keys = self.data[cat]['roles'].keys()
    roles_with_fact = []
    for i in all_role_keys:
      base = self.data[cat]['roles'][i]['unique']
      for b in base:
        if fact == b[1]:
          roles_with_fact.append(i)
    roles_with_fact = list(set(roles_with_fact))
    return roles_with_fact

    def get_fact(self, fact, cat='pre'):
      """ Returns the value of a fact """
      role = self.find_fact_in_role(fact)

  def get_tree_data(self, base, role_keys, tabs=0):
    """Traverse cal tree and return."""

    for rk in role_keys:
      # Must mean there exists a sub tree?
      if rk == 'sub':
        continue
      lab_str = str(rk)

      try:
        base_keys = base[rk]['val'].keys()
        if len(base_keys) == 0 and len(base[rk]['sub']) == 0:
            continue
        else:
          date_str = ''
          val_str = ''
          for i in base_keys:
            date_str += str(i)
          for bk in base_keys:
            if base[rk]['val'][bk] == None:
              continue
            if isinstance(base[rk]['val'][bk], float):
              val_str += str(base[rk]['val'][bk])
            else:
              val_str += base[rk]['val'][bk].encode('utf-8')
            val_str += '\t\t'
          print(lab_str)
          print(tab_str + '\t' + date_str)
          print(tab_str + '\t' + val_str)
      except KeyError:
        pass
      # Continue to print for sub tree?
      if len(base[rk]['sub']) > 0:
        rk_base = base[rk]['sub']
        rk_base_keys = rk_base.keys()
        self.traverse_print_tree(rk_base, rk_base_keys, tabs=tabs+1)

  def get_financial_position(self):
      balance_sheet_role = self.find_fact_in_role('AssetsAbstract')[0]
      #print self.data['pre']['roles'][balance_sheet_role]['tree']['StatementOfFinancialPositionAbstract']['sub'].keys()
      return self.data['pre']['roles'][balance_sheet_role]['tree']['StatementOfFinancialPositionAbstract']['sub']

  def get_balance_sheet_value(self,key):
      #search key under sub until desired key is found
      financial_pos_node = self.get_financial_position()
      return self.search_for_key(key, financial_pos_node)

  def search_for_key(self,key,pos):
      if len(pos) == 0:
          return None
      for child in pos.keys():
          if child == key:
              return pos[child]['val']
          else:
              child_result = self.search_for_key(key, pos[child]['sub'])
              if child_result is not None: 
                  return child_result


  def find_key_paths(self, base=None, cat='pre', path=[]):
      if base == None: 
          base = self.data[cat]['roles']
          self.find_key_paths(base=base)
      elif type(base) is tuple:
          self.path_pairs.append([base[1], path])
      elif type(base) is list:
          for i in base:
              next_path = path + [i]
              self.find_key_paths( base=i, path=next_path)
      else:
        for rk in base.keys():
            #print rk
            if type(base[rk]) == str: 
                return base[rk]
            elif type(base[rk]) == list:
                for i in base[rk]:
                    next_path = path + [i]
                    self.find_key_paths(base=base[rk], path=next_path)
                    #self.find_key_paths(base[rk])
            else:
                if base[rk] != None and base[rk].keys() != None and base[rk].keys() != []:
                    next_path = path + [rk]
                    self.find_key_paths(base=base[rk], path=next_path)

      





