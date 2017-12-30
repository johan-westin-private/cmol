#!/usr/bin/env python

import os

import pybel

ROUTE = '!b97-d3 def2-tzvp def2-tzvp/j ecp(def2-tzvp,def2-tzvp/j) slowconv nososcf'


def mkinp_orca(mols, bq=(), route=""):
    etab = pybel.ob.OBElementTable()
    res = list()
    res.append(route + "\n")
    res.append('*xyz 0 1\n')
    for i in range(len(mols)):
        if i in bq:
            bqflag = ':'
        else:
            bqflag = ' '
        for j in range(len(mols[i].atoms)):
            atom = mols[i].atoms[j].OBAtom
            res.append('%2s %s % 10.6f % 10.6f % 10.6f\n' % (etab.GetSymbol(atom.GetAtomicNum()),
                                                             bqflag, atom.GetX(), atom.GetY(), atom.GetZ()))
    res.append('*\n')
    return res


if __name__ == '__main__':
    from optparse import OptionParser
    from glob import glob

    usage = "%prog [-h|--help] [-b|--bsse]  <name>"

    description = "Script for construction of ORCA inputs from XYZ files. Optionally creates input files for BSSE correction. Reads <name>-d???.xyz and <name>-m??.xyz files."

    parser = OptionParser(usage=usage, description=description)

    # parser.add_option
    parser.add_option('-b', '--bsse', action="store_true", dest='bsse',
                      help='Flag to create input files for BSSE correction.', default=False)
    parser.add_option('-r', '--route', dest='route', help='ORCA instructions.', type='str', default=ROUTE)

    (m_options, m_args) = parser.parse_args()

    # arg checks
    if not len(m_args) == 1:
        parser.error('Single argument <name> required.\nGet more help with -h option.')
    name = m_args[0]

    # ..go
    m_xyz_d = glob('%s-d???.xyz' % name)
    assert m_xyz_d, "Could not find files matching mask %s-d???.xyz" % name
    m_xyz_m = []
    if not m_options.bsse:
        m_xyz_m = glob('%s-m??.xyz' % name)
        assert m_xyz_m, "Could not find files matching mask %s-m??.xyz" % name

    if m_options.bsse:
        # create name-d???-m0-1.inp, name-d???-m0.inp and name-d???-m1.inp
        for m_xyzfile in m_xyz_d:
            m_basename = os.path.splitext(m_xyzfile)[0]
            m_mols = [m for m in pybel.readfile('xyz', m_xyzfile)]
            assert len(m_mols) == 2, "Expected 2 molecules in file %s, found %i" % (m_xyzfile, len(m_mols))
            with open(m_basename + '-m0-1.inp', 'w') as m_f:
                m_f.writelines(mkinp_orca(m_mols, route=m_options.route))
            with open(m_basename + '-m0.inp', 'w') as m_f:
                m_f.writelines(mkinp_orca(m_mols, (1,), route=m_options.route))
            with open(m_basename + '-m1.inp', 'w') as m_f:
                m_f.writelines(mkinp_orca(m_mols, (0,), route=m_options.route))
    if not m_options.bsse:
        # create name-d???.inp amd name-m??.inp
        for m_xyzfile in m_xyz_d + m_xyz_m:
            m_basename = os.path.splitext(m_xyzfile)[0]
            m_mols = [m for m in pybel.readfile('xyz', m_xyzfile)]
            with open(m_basename + '.inp', 'w') as m_f:
                m_f.writelines(mkinp_orca(m_mols, route=m_options.route))
