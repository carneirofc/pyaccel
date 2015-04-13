
import unittest
import numpy
import pyaccel
import trackcpp
import sirius

class TestLattice(unittest.TestCase):

    def setUp(self):
        self.element = pyaccel.elements.Element()
        self.the_ring = sirius.create_accelerator()

    def tearDown(self):
        pass

    def test_lengthlat(self):
        length = pyaccel.lattice.lengthlat(self.the_ring)
        self.assertAlmostEqual(length,518.396)

    def test_get_rf_frequency(self):
        self.assertAlmostEqual(pyaccel.lattice.get_rf_frequency(self.the_ring),499657944.80373, 4)

    def test_findspos(self):
        s = [0, 0, 0, 0, 0.5000, 1.0000, 3.4129, 3.4129,
            3.4129, 3.5129, 3.6229, 3.7729, 3.8929, 3.8929,
            4.0329, 4.2329, 4.4729, 4.6129, 4.7629, 4.9129]
        pos = pyaccel.lattice.findspos(self.the_ring, range(20))
        for i in range(20):
            self.assertAlmostEqual(pos[i], s[i])

        posicao = pyaccel.lattice.findspos(self.the_ring)
        ind = len(self.the_ring)-1
        self.assertAlmostEqual(posicao[ind], 518.3960)

    def test_flatlat(self):
        flat_elist = [self.element]*12
        elist = [self.element,self.element,[self.element,[self.element,
                [[self.element,self.element],self.element],self.element],
                self.element,[self.element,[self.element,]],self.element]]
        elist = pyaccel.lattice.flatlat(elist)
        self.assertEqual(elist, flat_elist)

    def test_buildlat(self):
        elist = [self.element,self.element,[self.element,[self.element,
                [[self.element,self.element],self.element],self.element],
                self.element,[self.element,[self.element,]],self.element]]
        lattice = pyaccel.lattice.buildlat(elist)
        self.assertTrue(isinstance(lattice, trackcpp.trackcpp.CppElementVector))

    def test_shiftlat(self):
        fam_name = 'end'
        start = len(self.the_ring)-1
        self.the_ring = pyaccel.lattice.shiftlat(self.the_ring, start)
        self.assertEqual(self.the_ring[0].fam_name, fam_name)

    def test_findcells(self):
        indices_pb = pyaccel.lattice.findcells(self.the_ring, 'polynom_b')
        self.assertEqual(len(indices_pb),len(self.the_ring))

        indices_bc = pyaccel.lattice.findcells(self.the_ring, 'polynom_b', [0, -0.0001586, -28.62886])
        for i in indices_bc:
            self.assertEqual(self.the_ring[i].fam_name,'bc')

        mia = [1, 327, 655, 983, 1311, 1639, 1967, 2295, 2623, 2951]
        indices_mia = pyaccel.lattice.findcells(self.the_ring, 'fam_name', 'mia')
        for i in range(len(mia)):
            self.assertEqual(indices_mia[i], mia[i])

    def test_getcellstruct(self):
        length = pyaccel.lattice.getcellstruct(self.the_ring, 'length')
        self.assertAlmostEqual(sum(length),518.396)

        fam_name = pyaccel.lattice.getcellstruct(self.the_ring, 'fam_name', range(20))
        for i in range(20):
            self.assertEqual(fam_name[i], self.the_ring[i].fam_name)

        polynom_b = pyaccel.lattice.getcellstruct(self.the_ring,'polynom_b',range(20),m=1)
        for i in range(20):
            self.assertEqual(polynom_b[i],self.the_ring[i].polynom_b[1])

        r_in = pyaccel.lattice.getcellstruct(self.the_ring,'r_in',range(20),m=1,n=1)
        for i in range(20):
            self.assertEqual(r_in[i],self.the_ring[i].r_in[1,1])

    def test_setcellstruct(self):
        self.the_ring = pyaccel.lattice.setcellstruct(self.the_ring, 'length', 1, 1)
        self.assertEqual(self.the_ring[1].length, 1)

        self.the_ring = pyaccel.lattice.setcellstruct(self.the_ring, 'fam_name', [1,2], ['test1','test2'])
        self.assertEqual(self.the_ring[1].fam_name, 'test1')
        self.assertEqual(self.the_ring[2].fam_name, 'test2')

        self.the_ring = pyaccel.lattice.setcellstruct(self.the_ring, 'polynom_b', [1,2], [[1,1,1],[2,2,2]] )
        self.assertEqual(self.the_ring[1].polynom_b[0], 1)
        self.assertEqual(self.the_ring[2].polynom_b[0], 2)

        self.the_ring = pyaccel.lattice.setcellstruct(self.the_ring, 'polynom_b', [1,2], [[1,1,1]] )
        self.assertEqual(self.the_ring[1].polynom_b[0], 1)
        self.assertEqual(self.the_ring[2].polynom_b[0], 1)

        self.the_ring = pyaccel.lattice.setcellstruct(self.the_ring, 'r_in', 1, [numpy.zeros((6,6))] )
        self.assertEqual(self.the_ring[1].r_in[0,0], 0)

    def test_finddict(self):
        names_dict=pyaccel.lattice.finddict(self.the_ring, 'fam_name')
        for key in names_dict.keys():
            ind=names_dict[key]
            for i in ind:
                self.assertEqual(self.the_ring[i].fam_name, key)

def lattice_suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLattice)
    return suite


def get_suite():
    suite_list = []
    suite_list.append(lattice_suite())
    return unittest.TestSuite(suite_list)
