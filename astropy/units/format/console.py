# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Handles the "Console" unit format.
"""


from . import base, utils


class Console(base.Base):
    """
    Output-only format for to display pretty formatting at the
    console.

    For example::

      >>> import astropy.units as u
      >>> print(u.Ry.decompose().to_string('console'))  # doctest: +FLOAT_CMP
      2.1798721*10^-18 m^2 kg s^-2
      >>> print(u.Ry.decompose().to_string('console', inline=False))  # doctest: +FLOAT_CMP
                       m^2 kg
      2.1798721*10^-18 ------
                        s^2
    """

    _times = "*"
    _line = "-"
    _space = " "

    @classmethod
    def _format_mantissa(cls, m):
        return m

    @classmethod
    def format_exponential_notation(cls, val, format_spec=".8g"):
        """
        Formats a value in exponential notation.

        Parameters
        ----------
        val : number
            The value to be formatted

        format_spec : str, optional
            Format used to split up mantissa and exponent

        Returns
        -------
        string : str
            The value in exponential notation in a this class's format.
        """
        m, ex = utils.split_mantissa_exponent(val, format_spec)

        parts = []
        if m:
            parts.append(cls._format_mantissa(m))

        if ex:
            parts.append(f"10{cls._format_superscript(ex)}")

        return cls._times.join(parts)

    @classmethod
    def _format_fraction(cls, scale, nominator, denominator):
        fraclength = max(len(nominator), len(denominator))
        f = f"{{0:<{len(scale)}s}}{{1:^{fraclength}s}}"

        return "\n".join(
            (
                f.format("", nominator),
                f.format(scale, cls._line * fraclength),
                f.format("", denominator),
            )
        )

    @classmethod
    def to_string(cls, unit, inline=True):
        if unit.scale == 1:
            s = ""
        else:
            # Non-unity scale happens mostly for decomposed units.
            # E.g., u.Ry.decompose() gives "2.17987e-18 kg m2 / s2".
            s = cls.format_exponential_notation(unit.scale)

        # Take care that dimensionless does not have bases (but can
        # have a scale; e.g., u.percent.decompose() gives "0.01").
        if len(unit.bases):
            if s:
                s += cls._space
            if inline:
                nominator = zip(unit.bases, unit.powers)
                denominator = []
            else:
                nominator, denominator = utils.get_grouped_by_powers(
                    unit.bases, unit.powers
                )
            if len(denominator):
                if len(nominator):
                    nominator = cls._format_unit_list(nominator)
                else:
                    nominator = "1"
                denominator = cls._format_unit_list(denominator)
                s = cls._format_fraction(s, nominator, denominator)
            else:
                nominator = cls._format_unit_list(nominator)
                s += nominator

        return s
