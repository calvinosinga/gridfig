
import numpy as np
from typing import Optional, Union, List
class StyleGrid:

    def __init__(self, dg):
        shape = dg.getShape()
        # figure-level styles
        self.fstyles = {} # dict of style elements
        self.astyles = np.empty(shape, dtype = object)
        self.pstyles = np.empty(shape, dtype = object)
        self.astyles_all = {}
        for i in range(shape[0]):
            for j in range(shape[1]):
                self.astyles[i, j] = dict()
                p_dict = {}
                for k in range(len(dg.panels[i, j])):
                    pprop = dg.panels[i, j].panel_prop
                    pval = dg.panels[i, j][k][pprop].unique()
                    if len(pval) > 1:
                        raise ValueError("panel value has multiple values...")
                    
                    p_dict[pval[0]] = {}
                self.pstyles[i, j] = p_dict
        
        return
    
    def _set(self, _dct, _name, _args):
        if _name not in _dct:
            _dct[_name] = dict()
        _dct[_name].update(_args)
        return
    
    def setFigStyle(self, name, args):
        self._set(self.fstyles, name, args)
        return
    
    def setAxStyle(self, panel_idx, name, args):
        self._set(self.astyles[panel_idx[0], panel_idx[1]], name, args)
        return
    
    def setAxStyleAll(self, name, args):
        self._set(self.astyles_all, name, args)
    
    def setPlotStyle(self, panel_idx, panel_val, name, args):
        self._set(self.pstyles[panel_idx[0], panel_idx[1]][panel_val], name, args)
        return
    


    def _dct_to_str(self, prefix, dct):
        dctstr = ''
        for k, v in dct.items():
            if isinstance(v, dict):
                dctstr += f"{prefix}{k}:\n"
                dctstr += self._dct_to_str('\t' + prefix, v)
            
            else:
                dctstr += f"{prefix}{k} = {v}\n"
        return dctstr
    
    def printFigStyles(self):
        out = self._dct_to_str('', self.fstyles)
        return out

    def printPanelStylesAll(self):
        out = self._dct_to_str('', self.astyles_all)
        return out
    
    def printPanelStyles(self):
        out = ''
        for i in range(self.astyles.shape[0]):
            for j in range(self.astyles.shape[1]):
                out += f'Panel ({i}, {j})\n'
                out += self._dct_to_str('\t', self.astyles[i, j])
        return out
    
    
    
    def __str__(self) -> str:


            
        out = 'FIGURE-LEVEL STYLES:\n\n'
        out += self.printFigStyles()

        out += '\nSTYLES FOR ALL PANELS\n\n'
        out += self.printPanelStylesAll()

        out += '\nSTYLES FOR SPECIFIC PANELS:\n\n'
        out += self.printPanelStyles()

        # out+= '\nPLOT-LEVEL STYLES:\n\n'
        # out
        return out



