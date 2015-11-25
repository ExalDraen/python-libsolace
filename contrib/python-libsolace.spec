%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define bname libsolace

Name:           python-%{bname}
Version:        2.0
Release:        1%{?dist}
Summary:        Python helpers for managing Solace appliances

Group:          Development/Libraries
License:        MIT
URL:            https://github.com/unixunion/%{name}/
Source0:        https://codeload.github.com/unixunion/%{name}/tar.gz/v%{version}

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
Requires:       pyparsing
Requires:       python-docopt
Requires:       python-lxml
Requires:       python-ordereddict
Requires:       python-simplejson
Requires:       PyYAML


%description
This is a set of Python helpers for managing Solace appliances.


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__rm} -rf $RPM_BUILD_ROOT/usr/bin
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}/%{bname}
%{__cp} %{bname}.yaml $RPM_BUILD_ROOT/%{_sysconfdir}/%{bname}


%clean
%{__rm} -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc LICENSE.md
%doc README.md
%{python_sitelib}/*
%{_sysconfdir}/%{bname}


%changelog
* Fri Sep 25 2015 Jiri Tyr <jiri.tyr@gmai.com> 2.0-1
- initial spec file
