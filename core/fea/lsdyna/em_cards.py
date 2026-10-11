"""R13 Volume III, EM chapter: explicit standard-width card schemas.

Blank fields remain None (solver defaults are not invented). Reserved columns
remain in place. RELTOL is real as described in the manual, despite the I typo
in the FEM/BEM overview tables. No generic EM_* layout inference is used.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class EmSchema:
    cards: tuple
    repeat: bool = False
    minimum: int = 1

    def card(self, index):
        if index >= len(self.cards) and not self.repeat:
            raise ValueError('too many electromagnetic data cards')
        names, types = self.cards[min(index, len(self.cards)-1)]
        names = tuple(names.split())
        return names + ('-',)*(8-len(names)), types + '-'*(8-len(types))


# EM_OUTPUT legacy fields: Ansys official TEAM 3/TEAM 20 reduced inputs.
# https://lsdyna.ansys.com/team3-d89/ (R13 documents only fields 1..7).
# MONOLITHIC extra rows: https://lsdyna.ansys.com/team13/
# These legacy options are retained, not reinterpreted as R13 solver options.
EM_SCHEMAS = {
    "EM_CONTROL": EmSchema((('EMSOL NUMLS MACRODT DIMTYPE NPERIO - NCYLFEM NCYLBEM', 'IIFII-II'),), repeat=False, minimum=1),
    "EM_CONTROL_TIMESTEP": EmSchema((('TSTYPE DTCONST LCID FACTOR TSMIN TSMAX RLCSF MECATS', 'IFIFFFII'),), repeat=False, minimum=1),
    "EM_CIRCUIT_SOURCE": EmSchema((('CIRCID CIRCTYP LCID R/F L/A C/to V0 T0', 'IIIFFFFF'), ('SIDCURR SIDVIN SIDVOUT PARTID', 'IIII')), repeat=False, minimum=2),
    "EM_CIRCUIT_ROGO": EmSchema((('ROGID SETID SETTYPE CURTYP', 'IIII'),), repeat=True, minimum=1),
    "EM_DATABASE_POINTOUT": EmSchema((('OUTLV DTOUT', 'IF'), ('PSID', 'I')), repeat=True, minimum=2),
    "EM_EOS_PERMEABILITY": EmSchema((('EOSID EOSTYPE LCID', 'III'),), repeat=False, minimum=1),
    "EM_EXTERNAL_FIELD": EmSchema((('FIELDID FTYPE FDEF LCIDX LCIDY LCIDZ', 'IIFIII'),), repeat=False, minimum=1),
    "EM_MAT_001": EmSchema((('MID MTYPE SIGMA EOSID - - DEATHT RDLTYPE', 'IIFI--FI'),), repeat=False, minimum=1),
    "EM_MAT_002": EmSchema((('MID MTYPE SIGMA EOSID MUREL EOSMU DEATHT', 'AIFIFIF'), ('- EOSID2', '-I')), repeat=False, minimum=1),
    "EM_OUTPUT": EmSchema((('MATS MATF SOLS SOLF MESH MEM TIMING D3PLOTASC', 'IIIIIIII'), ('MF2 GMV D3PLOTFOR TIMEHIST', 'IIII')), repeat=False, minimum=1),
    "EM_POINT_SET": EmSchema((('PSID PSTYPE VX VY VZ', 'IIFFF'), ('PID X Y Z POS', 'IFFFI')), repeat=True, minimum=2),
    "EM_SOLVER_BEM": EmSchema((('RELTOL MAXITE STYPE PRECON USELAST NCYLBEM', 'FIIIII'),), repeat=False, minimum=1),
    "EM_SOLVER_BEMMAT": EmSchema((('MATID - - - - - - RELTOL', 'I------F'),), repeat=False, minimum=1),
    "EM_SOLVER_FEM": EmSchema((('RELTOL MAXITE STYPE PRECON USELAST NCYCLFEM', 'FIIIII'),), repeat=False, minimum=1),
    "EM_SOLVER_FEMBEM": EmSchema((('RELTOL MAXITE FORCON', 'FII'),), repeat=False, minimum=1),
    "EM_SOLVER_FEMBEM_MONOLITHIC": EmSchema((('MTYPE STYPE ABSTOL RELTOL MAXIT GMRES_RST - DEBUG', 'IIFFII-I'), ('- NEWT_STOL NEWT_ATOL NEWT_RTOL NEWT_MAXI', '-FFFI'), ('LS_ON LS_FTOL LS_GTOL LS_RTOL LS_SAMPL LS_NUM_SP LS_MAXFUN', 'IFFFIII')), repeat=False, minimum=1),
}
