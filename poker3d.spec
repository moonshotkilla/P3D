%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           poker3d
Version:        1.1.36
Release:        17%{?dist}
Summary:        Three dimensional multi-user online poker game

Group:          Amusements/Games
License:        GPLv2+
URL:            http://gna.org/projects/underware
#Source0:        http://download.gna.org/underware/sources/%{name}-%{version}.tar.gz
# Temporary Source0 URL until upstream fixes stable tarballs
Source0:        http://pok3d.net/unstable/poker3d_1.1.36.orig.tar.gz
Patch0:         %{name}-1.1.36-64bit.patch
Patch1:         %{name}-1.1.36-libexec.patch
Patch2:         %{name}-1.1.36-osg.patch
Patch3:         %{name}-1.1.36-gcc43.patch
Patch4:         %{name}-1.1.36-python26.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  ImageMagick desktop-file-utils
BuildRequires:  OpenSceneGraph-devel >= 0.9.8, osgal-devel >= 0.3
BuildRequires:  cal3d-devel osgcal-devel >= 0.1.37
BuildRequires:  python-devel SDL-devel libxml2-devel glib2-devel libtool
BuildRequires:  poker-engine-devel poker-network-devel >= 1.0.36
Requires:       poker-engine poker-network >= 1.0.36
Requires:       hicolor-icon-theme poker2d-common poker3d-data
Requires:       xwnc python-simplejson opengl-games-utils

%description
%{summary}.


%prep
%setup -q
%patch0 -p0 -b .64bit~
%patch1 -p0 -b .libexec~
%patch2 -p0 -b .osg~
%patch3 -p1 -b .gcc43~
%patch4 -p0 -b .python26~
autoreconf --force --install

# Avoid lib64 rpaths
#sed -i -e 's|"/lib /usr/lib|"/%{_lib} %{_libdir}|' configure

# Fix rpmlint warnings
find src -name "*.cpp" -exec chmod -x {} \;
find include -name "*.h" -exec chmod -x {} \;
chmod -x osgplugins/ddsrle/src/rle*

# Fix file encodings
iconv -f iso8859-1 -t utf-8 ChangeLog > ChangeLog.conv && mv -f ChangeLog.conv ChangeLog

# Remove shell bangs
pushd examples/poker
for file in $(find . -type f -name "*.py"); do
  cp $file $file.orig
  grep -v -e "^\#\!" $file.orig > $file
  rm -f $file.orig
done
popd

# Convert icon
convert poked_16_256.ico %{name}.png

# Create poker3d desktop file
cat > %{name}.desktop << EOF
[Desktop Entry]
Encoding=UTF-8
Name=%{name}
GenericName=Multiplayer online poker
GenericName[fr]=Poker multijoueur en ligne
Comment=3-D Poker Client
Exec=%{name}
Icon=%{name}.png
X-Miniicon=%{name}.png
X-DocPath=%{name}/index.html
Terminal=false
Type=Application
Categories=KDE;Game;CardGame;
EOF

# Create wrapper shell script
cat > %{name} << EOF
#!/bin/sh
. %{_datadir}/opengl-games-utils/opengl-game-functions.sh
checkDriOK %{name}
export LD_LIBRARY_PATH=%{_libdir}/%{name}
exec %{_libexecdir}/%{name}/%{name} "\$@"
EOF


%build
# relocate libraries because they are not meant to be shared by other apps
%configure --disable-static --libdir=%{_libdir}/%{name} \
    --with-poker-server-host=poker.pokersource.info \
    --with-poker-www-host=pokersource.info
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Remove libtool archive files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}/*.la
find $RPM_BUILD_ROOT%{python_sitearch} -name "*.la" -exec rm -f {} \;

# Install icon
install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps
install -pm 644 %{name}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps

# Install fedora desktop file
rm -f $RPM_BUILD_ROOT%{_datadir}/applications/*.desktop
desktop-file-install --vendor=fedora \
    --dir=$RPM_BUILD_ROOT%{_datadir}/applications \
    %{name}.desktop

# Install wrapper script
install -d $RPM_BUILD_ROOT%{_bindir}
install -m 755 %{name} $RPM_BUILD_ROOT%{_bindir}

# Relocate poker3d binary
install -d $RPM_BUILD_ROOT%{_libexecdir}/%{name}
mv $RPM_BUILD_ROOT%{_exec_prefix}/games/%{name} $RPM_BUILD_ROOT%{_libexecdir}/%{name}

# Remove unneeded files
rm -fr $RPM_BUILD_ROOT%{_includedir}/varseditor
rm -f  $RPM_BUILD_ROOT%{_datadir}/%{name}/data/PLACEHOLDER


%clean
rm -rf $RPM_BUILD_ROOT


%post
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
    %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README
%{_bindir}/%{name}
%{_libdir}/%{name}
%{_libexecdir}/%{name}
%{_datadir}/%{name}/*
%{_datadir}/applications/fedora-%{name}.desktop
%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{python_sitelib}/underware
%{python_sitearch}/*
%{_mandir}/man6/%{name}.6.gz


%changelog
* Tue Aug 25 2009 Alex Lancaster <alexlan[AT]fedoraproject org> - 1.1.36-17
- Rebuild for new openal to fix broken deps in rawhide

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.36-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.36-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 16 2009 Ralf Corsépius <corsepiu@fedoraproject.org> - 1.1.36-14
- Rework poker3d-1.1.36-gcc43.patch.
- Rebuild against OSG-2.8.0 + poker-eval-135.0-3.

* Tue Dec 02 2008 Christopher Stone <chris.stone@gmail.com> 1.1.36-13
- Add python26 patch

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.1.36-12
- Rebuild for Python 2.6

* Tue Sep 09 2008 Christopher Stone <chris.stone@gmail.com> 1.1.36-11
- Rebuild against OSG-2.6.0

* Fri May 16 2008 Ralf Corsépius <rc040203@freenet.de> - 1.1.36-10
- Rebuild against OSG-2.4.0.

* Thu Feb 21 2008 Christopher Stone <chris.stone@gmail.com> 1.1.36-9
- Add gcc43 patch

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.1.36-8
- Autorebuild for GCC 4.3

* Sun Nov 18 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-7
- Add python-simplejson to Requires

* Sat Nov 17 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-6
- Remove no longer needed ldconfig
- Add xwnc to Requires

* Fri Nov 16 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-5
- Add a wrapper script to invoke poker3d instead of using ld.so.conf

* Thu Nov 15 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-4
- Add patch to fix compile with OSG2.x

* Thu Nov 15 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-3
- Use a temporary %%SOURCE0 URL until upstream updates stable tarballs

* Tue Nov 06 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-2
- Update icon cache scriptlets

* Sun Oct 28 2007 Christopher Stone <chris.stone@gmail.com> 1.1.36-1
- Initial Fedora release
