#
# Conditional build:
%bcond_without	prof	# profiling library
#
%define		pkgname	cryptonite
Summary:	Cryptography Primitives sink
Summary(pl.UTF-8):	Zbiór prymitywów kryptograficznych
Name:		ghc-%{pkgname}
Version:	0.26
Release:	3
License:	BSD
Group:		Development/Languages
#Source0Download: http://hackage.haskell.org/package/cryptonite
Source0:	http://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	759be6bffbfc9bb4c525d9dac55f9f7c
URL:		http://hackage.haskell.org/package/cryptonite
BuildRequires:	ghc >= 6.12.3
BuildRequires:	ghc-base
BuildRequires:	ghc-basement >= 0.0.6
BuildRequires:	ghc-bytestring
BuildRequires:	ghc-deepseq
BuildRequires:	ghc-ghc-prim
BuildRequires:	ghc-memory >= 0.14.18
%if %{with prof}
BuildRequires:	ghc-prof >= 6.12.3
BuildRequires:	ghc-basement-prof >= 0.0.6
BuildRequires:	ghc-bytestring-prof
BuildRequires:	ghc-deepseq-prof
BuildRequires:	ghc-ghc-prim-prof
BuildRequires:	ghc-memory-prof >= 0.14.18
%endif
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
Requires:	ghc-base
Requires:	ghc-basement >= 0.0.6
Requires:	ghc-bytestring
Requires:	ghc-deepseq
Requires:	ghc-ghc-prim
Requires:	ghc-memory >= 0.14.18
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
A repository of cryptographic primitives:
- Symmetric ciphers: AES, DES, 3DES, CAST5, Blowfish, Twofish,
  Camellia, RC4, Salsa, XSalsa, ChaCha.
- Hash: SHA1, SHA2, SHA3, SHAKE, MD2, MD4, MD5, Keccak, Skein, Ripemd,
  Tiger, Whirlpool, Blake2
- MAC: HMAC, KMAC, Poly1305
- Asymmetric crypto: DSA, RSA, DH, ECDH, ECDSA, ECC, Curve25519,
  Curve448, Ed25519, Ed448
- Key Derivation Function: PBKDF2, Scrypt, HKDF, Argon2, BCrypt,
  BCryptPBKDF
- Cryptographic Random generation: System Entropy, Deterministic
  Random Generator
- Data related: Anti-Forensic Information Splitter (AFIS)

%description -l pl.UTF-8
Repozytorium prymitywów kryptograficznych:
- szyfry symetryczne: AES, DES, 3DES, CAST5, Blowfish, Twofish,
  Camellia, RC4, Salsa, XSalsa, ChaCha.
- funkcje skrótu: SHA1, SHA2, SHA3, SHAKE, MD2, MD4, MD5, Keccak,
  Skein, Ripemd, Tiger, Whirlpool, Blake2
- MAC: HMAC, KMAC, Poly1305
- kryptografia asymetryczna: DSA, RSA, DH, ECDH, ECDSA, ECC,
  Curve25519, Curve448, Ed25519, Ed448
- funkcje dla kluczy: PBKDF2, Scrypt, HKDF, Argon2, BCrypt,
  BCryptPBKDF
- kryptograficzne generatory liczb losowych: entropia systemowa,
  generator deterministyczny
- obsługa danych: Anti-Forensic Information Splitter (AFIS)

%package prof
Summary:	Profiling %{pkgname} library for GHC
Summary(pl.UTF-8):	Biblioteka profilująca %{pkgname} dla GHC
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	ghc-basement-prof >= 0.0.6
Requires:	ghc-bytestring-prof
Requires:	ghc-deepseq-prof
Requires:	ghc-ghc-prim-prof
Requires:	ghc-memory-prof >= 0.14.18

%description prof
Profiling %{pkgname} library for GHC. Should be installed when GHC's
profiling subsystem is needed.

%description prof -l pl.UTF-8
Biblioteka profilująca %{pkgname} dla GHC. Powinna być zainstalowana
kiedy potrzebujemy systemu profilującego z GHC.

%prep
%setup -q -n %{pkgname}-%{version}

%build
runhaskell Setup.hs configure -v2 \
	%{?with_prof:--enable-library-profiling} \
%ifarch x32
	--flags="-integer-gmp" \
%endif
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.hs build

runhaskell Setup.hs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d

runhaskell Setup.hs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
%{__rm} -rf %{name}-%{version}-doc
cp -a $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

runhaskell Setup.hs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf

find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -type d | %{__sed} "s|$RPM_BUILD_ROOT|%dir |" > %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.dyn_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" >> %{name}.files
find $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/%{pkgname}-%{version} -name '*.p_hi' | %{__sed} "s|$RPM_BUILD_ROOT||" > %{name}-prof.files

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files -f %{name}.files
%defattr(644,root,root,755)
%doc CHANGELOG.md README.md %{name}-%{version}-doc/*
%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf
%attr(755,root,root) %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.so
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*.a
%exclude %{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a

%if %{with prof}
%files prof -f %{name}-prof.files
%defattr(644,root,root,755)
%{_libdir}/%{ghcdir}/%{pkgname}-%{version}/*_p.a
%endif
