pyperl - Perl for Python
------------------------

This is an extension module for Python named `perl` that makes it possible 
to embed Perl interpreter(s) in any Python program.  It can be used to invoke
arbitrary Perl code, load any Perl modules and make calls directly
into Perl functions.  The Perl code invoked can call back into Python
as it see fit.

Also, this is a `Python::Object` perl module that makes it possible to 
embed Python in any Perl program; it is located in `Python-Object`
directory of this distribution.

You can select between 2 flavours for how to build the Perl for Python
extension.  Which flavour to build is selected by the presence (or
absence) of the `MULTI_PERL` file in this directory.  When `MULTI_PERL` is
enabled, each python thread will get its own separate perl
interpreter.  For `-DMULTI_PERL` builds an ithread eanabled perl is
required.  It means that if you build your own perl you should pass
the `-Duseithreads` option to `Configure`.

Perl 5.6.0 or better is required.  Python 1.5.2 or better is required.

Before you can build the Python extension module you should build the
Python::Object module for Perl.  This allow Perl to access Python
objects passed in from python calls.  This must be built first, since
perlmodule.c reference it and want to link with it.

Build instructions:
-------------------

- make sure your PATH is set up so that `perl` and `python`
reference the versions of the language interpreters that you want to use.

- Run these commands:

    - for `perl` python module:

	python setup.py install

    - for `Python::Object` perl module:

	cd Python-Object
	perl Makefile.PL
	make install

- You should now be able to run the test.py test script.

	python test.py

Known to work on Linux i386, Sparc Solaris and MS-Windows.

The API for using perl from python is documented in the `perlmodule.pod`
file.  The file can be converted to other formats with the `pod2*` tools
that come with perl.

The project home page is <http://www.zope.org/Wikis/zope-perl>.
Source code available at `https://github.com/vadrer/python-perl`.
Bug reports, suggestions and questions about this stuff are welcome there.

Copyright
---------
(C) 2000-2001 ActiveState.
(C) 2019      Vadim Konovalov

This code is distributed under the same terms as Perl; you can
redistribute it and/or modify it under the terms of either the GNU
General Public License or the Artistic License.

THIS SOFTWARE IS PROVIDED BY ACTIVESTATE `AS IS'' AND ANY EXPRESSED OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL ACTIVESTATE OR ITS CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
