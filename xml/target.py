from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time
import typing
from xml.etree import ElementTree as ET

from .element import Element


class Target(Element):
    """A target in a SALT proposal."""

    """XPaths for common nodes."""
    NAME = './{/PIPT/Proposal/Shared}Name'
    TARGET_CODE = './{/PIPT/Proposal/Shared}TargetCode'
    TARGET_TYPE = './{/PIPT/Proposal/Shared}TargetType'
    PM = './{/PIPT/Proposal/Shared}Coordinates/{/PIPT/Shared}ProperMotionAndEpoch'
    PM_RA = PM + '/{/PIPT/Shared}RightAscensionDot/{/PIPT/Shared}Value'
    PM_DEC = PM + '/{/PIPT/Shared}DeclinationDot/{/PIPT/Shared}Value'
    PM_EPOCH = PM + '/{/PIPT/Shared}Epoch'
    MAG_FILTER = './{/PIPT/Proposal/Shared}MagnitudeRange/{/PIPT/Proposal/Shared}Bandpass'
    MAG_MIN = './{/PIPT/Proposal/Shared}MagnitudeRange/{/PIPT/Proposal/Shared}Minimum'
    MAG_MAX = './{/PIPT/Proposal/Shared}MagnitudeRange/{/PIPT/Proposal/Shared}Maximum'
    FINDING_CHART = './{/PIPT/Proposal/Shared}FindingChart'
    FINDING_CHART_PATH = './{/PIPT/Proposal/Shared}FindingChart/{/PIPT/Proposal/Shared}Path'

    @property
    def name(self) -> str:
        """Returns the name of this Target.

        Returns:
            Name of this Target.
        """
        return self.get(Target.NAME)

    @name.setter
    def name(self, v: str):
        """Sets new name for this Target.

        Args:
            v: New name.
        """
        self.set(Target.NAME, v)

    @property
    def code(self) -> str:
        """Returns the code of this Target.

        Returns:
            Code of this Target.
        """
        return self.get(Target.TARGET_CODE)

    @code.setter
    def code(self, v: str):
        """Sets new code for this Target.

        Args:
            v: New code.
        """
        self.set(Target.TARGET_CODE, v)

    @property
    def type(self) -> str:
        """Returns the type of this Target.

        Returns:
            Type of this Target.
        """
        return self.get(Target.TARGET_TYPE)

    @type.setter
    def type(self, v: str):
        """Sets new type for this Target.

        Args:
            v: New type.
        """
        self.set(Target.TARGET_TYPE, v)

    @property
    def coordinates(self) -> SkyCoord:
        """Returns coordinates of this target."""

        # coordinates
        coords = self.root.find('./{/PIPT/Proposal/Shared}Coordinates'.format(**self.namespaces))

        # RA
        ra = coords.find('./{/PIPT/Shared}RightAscension'.format(**self.namespaces))
        ra_h = ra.find('./{/PIPT/Shared}Hours'.format(**self.namespaces)).text
        ra_m = ra.find('./{/PIPT/Shared}Minutes'.format(**self.namespaces)).text
        ra_s = ra.find('./{/PIPT/Shared}Seconds'.format(**self.namespaces)).text

        # Dec
        dec = coords.find('./{/PIPT/Shared}Declination'.format(**self.namespaces))
        dec_sign = dec.find('./{/PIPT/Shared}Sign'.format(**self.namespaces)).text
        dec_d = dec.find('./{/PIPT/Shared}Degrees'.format(**self.namespaces)).text
        dec_m = dec.find('./{/PIPT/Shared}Arcminutes'.format(**self.namespaces)).text
        dec_s = dec.find('./{/PIPT/Shared}Arcseconds'.format(**self.namespaces)).text

        # equinox
        equinox = float(coords.find('./{/PIPT/Shared}Equinox'.format(**self.namespaces)).text)

        # return SkyCoord
        return SkyCoord('%s:%s:%s %s%s:%s:%s' % (ra_h, ra_m, ra_s, dec_sign, dec_d, dec_m, dec_s),
                        unit=(u.hourangle, u.deg), equinox=equinox)

    @coordinates.setter
    def coordinates(self, v: SkyCoord):
        """Sets coordinates of this target.

        Args:
            v: New coordinates.
        """

        # coordinates
        coords = self.root.find('./{/PIPT/Proposal/Shared}Coordinates'.format(**self.namespaces))

        # RA
        hms = v.ra.hms
        ra = coords.find('./{/PIPT/Shared}RightAscension'.format(**self.namespaces))
        ra.find('./{/PIPT/Shared}Hours'.format(**self.namespaces)).text = '%d' % hms.h
        ra.find('./{/PIPT/Shared}Minutes'.format(**self.namespaces)).text = '%d' % hms.m
        ra.find('./{/PIPT/Shared}Seconds'.format(**self.namespaces)).text = '%f' % hms.s

        # Dec
        dms = v.dec.dms
        dec = coords.find('./{/PIPT/Shared}Declination'.format(**self.namespaces))
        dec.find('./{/PIPT/Shared}Sign'.format(**self.namespaces)).text = '-' if dms.d < 0 else ''
        dec.find('./{/PIPT/Shared}Degrees'.format(**self.namespaces)).text = '%d' % abs(dms.d)
        dec.find('./{/PIPT/Shared}Arcminutes'.format(**self.namespaces)).text = '%d' % abs(dms.m)
        dec.find('./{/PIPT/Shared}Arcseconds'.format(**self.namespaces)).text = '%f' % abs(dms.s)

        # equinox
        coords.find('./{/PIPT/Shared}Equinox'.format(**self.namespaces)).text = '%f' % v.equinox \
            if v.equinox else "2000"

    @property
    def pm_ra(self) -> float:
        """Returns proper motion in RA."""
        return float(self.get(Target.PM_RA, default=0.))

    @pm_ra.setter
    def pm_ra(self, v: float):
        """Set proper motion in RA.

        Args:
            v: New proper motion in RA.
        """
        self.set(Target.PM_RA, str(v))

    @property
    def pm_dec(self) -> float:
        """Returns proper motion in Dec."""
        return float(self.get(Target.PM_DEC, default=0.))

    @pm_dec.setter
    def pm_dec(self, v: float):
        """Set proper motion in Dec.

        Args:
            v: New proper motion in Dec.
        """
        self.set(Target.PM_DEC, str(v))

    @property
    def epoch(self) -> typing.Union[Time, None]:
        """Returns epoch for coordinates."""
        time = self.get(Target.PM_EPOCH, default=0.)
        return Time(time) if time != 0 else None

    @epoch.setter
    def epoch(self, v: Time):
        """Set epoch for coordinates.

        Args:
            v: New epoch.
        """
        self.set(Target.PM_EPOCH, v.isot)

    @property
    def mag_filter(self) -> str:
        """Returns filter, in which given magnitudes were measured."""
        return self.get(Target.MAG_FILTER)

    @mag_filter.setter
    def mag_filter(self, v: str):
        """Set filter, in which given magnitudes were measured.

        Args:
            v: New filter.
        """
        self.set(Target.MAG_FILTER, v)

    @property
    def mag_min(self) -> float:
        """Returns minimum magnitude in given filter."""
        return float(self.get(Target.MAG_MIN))

    @mag_min.setter
    def mag_min(self, v: float):
        """Set minimum magnitude in given filter.

        Args:
            v: Minimum magnitude.
        """
        self.set(Target.MAG_MIN, str(v))
        
    @property
    def mag_max(self):
        """Returns maximum magnitude in given filter."""
        return float(self.get(Target.MAG_MAX))

    @mag_max.setter
    def mag_max(self, v: float):
        """Set maximum magnitude in given filter.

        Args:
            v: Maximum magnitude.
        """
        self.set(Target.MAG_MAX, str(v))

    @property
    def finding_charts(self) -> typing.List[str]:
        """Returns list of filenames of finding charts attached to this target.

        Returns:
            List of finding charts.
        """
        return [fc.text for fc in self.root.findall(Target.FINDING_CHART_PATH.format(**self.namespaces))]

    @finding_charts.setter
    def finding_charts(self, charts: typing.Union[str, typing.List[str]]):
        """Sets the finding chart(s) for this target.

        Args:
            charts: Either a single filename or a list of filenames for finding charts.
        """

        # we want a list of finding charts
        charts = [charts] if isinstance(charts, str) else charts

        # remove all from XML
        for fc in self.root.findall(Target.FINDING_CHART.format(**self.namespaces)):
            self.root.remove(fc)

        # add new
        for fc in charts:
            chart = ET.Element('{/PIPT/Proposal/Shared}FindingChart'.format(**self.namespaces))
            path = ET.Element('{/PIPT/Proposal/Shared}Path'.format(**self.namespaces))
            path.text = fc
            chart.append(path)
            self.root.append(chart)


__all__ = ['Target']
