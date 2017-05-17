###
#
# Command-line tests written in Python.
# Do 
#    >  python3 test.py ../../build/include_gardener ../test_files/
# to run the tests
#
# The first argument is used to defines the include_gardener executable,
# the second one defines where test-tree / files are located.
#
###
import unittest
import sys
import tempfile
import pygraphviz as pgv
import pygraphml  as pgml

from subprocess import Popen,PIPE
from os.path import abspath

class GardenerTestCases(unittest.TestCase):

    # default paths
    G_PATH="../../build/include_gardener"
    T_PATH="../test_files/"

    def setUp( self ):
        """Nothing to setup here"""


    def tearDown( self ):
        """Nothing to tear down here"""


    def build_reference_graph( self ):
        """ Builds a reference graph which shall be the same
            than the graph of ../test_files.

            A PyGraphml graph is returned.
        """
        g = pgml.Graph()

        f_1_c       = g.add_node( "1" )
        f_2_c       = g.add_node( "2" )
        f_3_c       = g.add_node( "3" )
        existing_h  = g.add_node("4")
        iostream    = g.add_node("5")
        lib_f_1_h   = g.add_node("6")
        lib_f_2_h   = g.add_node("7")
        lib_f_3_h   = g.add_node("8")
        lib2_f_4_h  = g.add_node("9")
        lib2_f_1_h  = g.add_node("10")

        e_1_x       = g.add_node("11")
        e_2_y       = g.add_node("12")

        f_1_c      ['key1'] = 'src/f_1.c'
        f_2_c      ['key1'] = 'src/f_2.c'
        f_3_c      ['key1'] = 'src/f_3.c'
        existing_h ['key1'] = '../non/existing.h'
        iostream   ['key1'] = 'iostream'
        lib_f_1_h  ['key1'] = 'inc/lib/f_1.h'
        lib_f_2_h  ['key1'] = 'inc/lib/f_2.h'
        lib_f_3_h  ['key1'] = 'inc/lib/f_3.h'
        lib2_f_4_h ['key1'] = 'inc/lib2/f_4.h'
        lib2_f_1_h ['key1'] = 'inc/lib2/f_1.h'
        e_1_x      ['key1'] = 'inc/lib/e_1.x'
        e_2_y      ['key1'] = 'inc/lib/e_2.y'

        g.add_edge( f_3_c, existing_h     )
        g.add_edge( f_3_c, iostream       )
        g.add_edge( f_2_c, lib2_f_1_h     )
        g.add_edge( f_1_c, iostream       )
        g.add_edge( f_1_c, lib_f_2_h      )
        g.add_edge( f_1_c, lib_f_1_h      )
        g.add_edge( lib_f_2_h, lib_f_1_h  )
        g.add_edge( lib_f_1_h, lib_f_3_h  )
        g.add_edge( lib_f_1_h, lib2_f_4_h )
        g.add_edge( lib_f_3_h, lib_f_1_h  )
        return g


    def compare( self, G1, G2 ):
        """ Compares two PyGraphml graphs by using PyUnittest's 
            assert methods.
        """

        nodes1 = G1.nodes()
        nodes2 = G2.nodes()
        self.assertEqual( len( nodes1 ), len( nodes2 ) )
        for n1 in nodes1:
            found = False

            src1 = n1['key1']
            src2 = ""
            dst1 = []
            dst2 = []

            # get all children
            for c1 in G1.children( n1 ):
                dst1.append( c1['key1'] )

            # search for the src in the second list
            for n2 in nodes2:
                src2 = n2['key1']

                if src1 == src2:
                    found = True
                    # get all children
                    for c2 in G2.children( n2 ):
                        dst2.append( c2['key1'] )
                    break

            self.assertTrue( found )
            self.assertEqual( src1, src2 )
            self.assertCountEqual( dst1, dst2 )


    def test_showsUnrecognisedOption( self ):
        """Tests "include_gardener --xyz"

        The test expects an unrecognised option information.
        """
        pipe = Popen( [ self.G_PATH, "--xyz" ], stderr=PIPE )
        result = pipe.communicate()[1].decode("utf-8")
        self.assertEqual( result, "unrecognised option '--xyz'\n" )


    def test_printHelp1( self ):
        """Tests "include_gardener -h"

        The test expects at least 'Options:' in stdout.
        """
        pipe = Popen( [ self.G_PATH, "-h" ], stdout=PIPE  )
        result = pipe.communicate()[0].decode("utf-8")
        self.assertIn( "Options:", result )


    def test_printHelp2( self ):
        """Tests "include_gardener --help"

        The test expects at least 'Options:' in stdout.
        """
        pipe = Popen( [ self.G_PATH, "--help" ], stdout=PIPE  )
        result = pipe.communicate()[0].decode("utf-8")
        self.assertIn( "Options:", result )


    def test_Version1( self ):
        """Tests "include_gardener -v"

        The test expects at least 'Version' in stdout.
        """
        pipe = Popen( [ self.G_PATH, "-v" ], stdout=PIPE  )
        result = pipe.communicate()[0].decode("utf-8")
        self.assertIn( "Version", result )


    def test_Version2( self ):
        """Tests "include_gardener --version"

        The test expects at least 'Version' in stdout.
        """
        pipe = Popen( [ self.G_PATH, "--version" ], stdout=PIPE  )
        result = pipe.communicate()[0].decode("utf-8")
        self.assertIn( "Version", result )


    def test_SimpleCallWithSinglePath( self ):
        """ Tests "include_gardener test_files"

        The test expects that the result can be read by pygraphviz
        and that there is at least one node.
        """
        pipe = Popen( [ self.G_PATH, self.T_PATH ], stdout=PIPE  )
        graph_str1 = pipe.communicate()[0].decode("utf-8")
        G = pgv.AGraph( graph_str1 )

        # the first node shall not be None ...
        n = G.get_node(1)
        self.assertNotEqual( n, None )

        # ... and the default format shall be dot
        pipe = Popen( [ self.G_PATH, self.T_PATH, '-f', 'dot' ], stdout=PIPE  )
        graph_str2 = pipe.communicate()[0].decode("utf-8")
        self.assertEqual( graph_str1, graph_str2 )


    def test_SimpleCallWithSinglePath_GraphmlOutput( self ):
        """ Tests "include_gardener test_files -f xml -I test_files/inc"

        The test expects that the result can be read by graphml
        and that there is at least one node.
        """
        pipe = Popen( [ self.G_PATH, self.T_PATH,
            '-f', 'xml', '-I', self.T_PATH + '/inc/' ], stdout=PIPE  )
        graphml_str = pipe.communicate()[0]
        temp = tempfile.NamedTemporaryFile()
        temp.write( graphml_str )
        temp.flush()
        parser = pgml.GraphMLParser()

        # get the result from the system call:
        g1 = parser.parse( temp.name )

        # get a reference graph
        g2 = self.build_reference_graph()

        # both graphs shall be the same
        self.compare( g1, g2 )

if __name__ == "__main__":
    if len( sys.argv ) > 2:
        GardenerTestCases.T_PATH = abspath( sys.argv.pop() )
        GardenerTestCases.G_PATH = abspath( sys.argv.pop() )
    unittest.main() # run all tests

