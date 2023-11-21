#
# MIT License
#
# (C) Copyright 2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
Name: @NAME@
License: MIT
Summary: System service that manages Squashfs images projected via iSCSI for IMS, PE, and other ancillary images similar to PE.
Group: System/Management
Version: @VERSION@
Release: @RELEASE@
Source: %{name}-@VERSION@-@RELEASE@.tar.bz2
BuildArch: @ARCH@
Vendor: HPE
BuildRequires: python-rpm-macros
BuildRequires: systemd-rpm-macros
BuildRequires: python3-base
Requires: python3-base
Requires: python3-virtualenv
Requires: systemd

%define _unpackaged_files_terminate_build 0
%define _systemdsvcdir /usr/lib/systemd/system
%define install_dir /usr/lib/%{name}
%define stage_dir /tmp/%{name}-wheels

%description
System service that manages Squashfs images projected via iSCSI for IMS, PE, and other ancillary images similar to PE.

%prep
%setup -q -n %{name}-@VERSION@-@RELEASE@

%build

%install
mkdir -p %{buildroot}%{stage_dir}/ %{buildroot}%{_systemdsvcdir}/
cp wheels/*.whl %{buildroot}%{stage_dir}/
cp etc/%{name}.service %{buildroot}%{_systemdsvcdir}/

%clean
rm -rf %{buildroot}

%files
%config(missingok) %{stage_dir}
%{_systemdsvcdir}/%{name}.service

%pre
%if 0%{?suse_version}
%service_add_pre %{name}.service
%endif

%post
%if 0%{?suse_version}
%service_add_post %{name}.service
%else
%systemd_post %{name}.service
%endif
virtualenv %{install_dir}
%{install_dir}/bin/pip3 install %{stage_dir}/*.whl
rm -Rf %{stage_dir}

%preun
%if 0%{?suse_version}
%service_del_preun %{name}.service
%else
%systemd_preun %{name}.service
%endif
rm -Rf %{install_dir}

%postun
%if 0%{?suse_version}
%service_del_postun %{name}.service
%else
%systemd_postun_with_restart %{name}.service
%endif

%changelog
