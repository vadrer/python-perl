use ExtUtils::MakeMaker;

# perl -MPortable -w Makefile.PL

chomp(my $pyinc = `python ./pyinc.py`);
print "Picking up pyton include files from \"$pyinc\"\n";

my @define;
my @libs;

#push(@define, "MULTI_PERL"); # if 1 and -f "../MULTI_PERL";

#if (-f "../BOOT_FROM_PERL") {
#    push(@define, "BOOT_FROM_PERL");
#
#    ...;
#
#    # XXX need to find the location of python.a, and this
#    # is obviously not the right way...
#    my $pylib = $pyinc;
#    $pylib =~ s/include/lib/;
#    $pylib =~ m,/(python[^/]+)$, || die;
#    $pylib .= "/config";
#    push(@libs, "-L$pylib -l$1");
#
#    push(@extra, OBJECT => "Object.o /local/python/1.5.2-thr/lib/python1.5/site-packages/perl.so");
#}

my @c = qw(lang_map svrv_object perlmodule lang_lock perlxsi try_perlapi);            # thrd_ctx 

if ($^O eq 'MSWin32') {
    my @pl = (
	# candidates where py lib located, eg [...]\\..\\libs\\libpython36.a
	"$pyinc\\..\\libs\\libpython*.a", 
	"$pyinc\\..\\libs\\python*.lib",
    );
    my $pylib = [(grep{-f} map {glob($_)} @pl),'?']->[0];
    if ($pylib eq '?') {die "can not find lib in @pl"}

    push @libs, "\"$pylib\"";
    push @extra, FUNCLIST => [qw(boot_Python__Object newPerlPyObject_noinc newPerlPyObject_inc)];
    push @extra, OBJECT => join ' ', 'Object.o', map {"$_.o"} @c;
}

if (@define) {
    push(@extra, DEFINE => join(" ", map "-D$_", @define));
}
if ($#libs>-1) {
    push(@extra, LIBS => \@libs);
}

sub MY::postamble {
    return join '', map {<<"EOS"} @c;
$_\$(OBJ_EXT) : ../$_.c
	\$(CCCMD) \$(CCCDLFLAGS) "-I\$(PERL_INC)" \$(PASTHRU_DEFINE) \$(DEFINE) ../$_.c
EOS
}

WriteMakefile(
    NAME	 => 'Python::Object',
    VERSION_FROM => 'Object.pm',
    INC          => "-I\"$pyinc\" -I.. ",
    # nope; CCFLAGS       => "-fleading-underscore",
    @extra,
    dist         => { COMPRESS => 'gzip -9f', SUFFIX => 'gz', },
);
