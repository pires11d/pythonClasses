"""Module that contains classes that represent the chemical components of a system."""


from collections import OrderedDict
from Geometry import Circle


class Substance:
    def __init__(self, name):
        self.Name = str(name)
        self.Temperature = 298.15
        self.Pressure = 101325.0
        self.MolarMass = None
        self.Density0 = None
        self.Viscosity0 = None
        self.SpecificHeat0 = None
        self.Diffusivity0 = None

    def Density(self, T=298.15):
        return self.Density0

    def Viscosity(self, T=298.15):
        return self.Viscosity0

    def SpecificHeat(self, T=298.15):
        return self.SpecificHeat0

    def Diffusivity(self, T=298.15):
        return self.Diffusivity0


class Mixture:
    def __init__(self, components):
        self.Components = components
        self.ComponentNames = [c.Name for c in self.Components]
        self.wi = None
        self.zi = None
        self.V = None
        self.M = None
        self.N = None
        self.Temperature = 298.15
        self.Pressure = 101325.0
        self._To = 273.15
        self._Po = 101325.0

    @property
    def MolarMass(self):
        MM = 0
        for i,MMi in enumerate(self.MolarMasses):
            MM += self.MolarFractions[i] * MMi
        return MM

    @property
    def MolarMasses(self):
        MMi = []
        for c in self.Components:
            MMi.append(c.MolarMass)
        return OrderedDict(zip(self.ComponentNames, MMi))

    @property
    def MassFractions(self):
        wi = []
        if self.wi is None:
            for i, MMi in enumerate(self.MolarMasses.values()):
                den = 0
                num = self.MolarFractions[i] * MMi
                for j, MMj in enumerate(self.MolarMasses.values()):
                    den += self.MolarFractions[j] * MMj
                wi.append(num / den)
        else: 
            wi = self.wi
        return wi

    @property
    def MolarFractions(self):
        zi = []
        if self.zi is None:
                for i, MMi in enumerate(self.MolarMasses.values()):
                    den = 0
                    num = self.MassFractions[i] / MMi
                    for j, MMj in enumerate(self.MolarMasses.values()):
                        den += self.MassFractions[j] / MMj
                    zi.append(num / den)
        else:
            zi = self.zi
        return zi

    @property
    def Mass(self):
        if self.M is None:
            if self.N is None:
                M = self.V * self.Density
            else:
                M = self.N * self.MolarMass
        else:
            M = self.M
        return M

    @property
    def Volume(self):
        if self.V is None:
            if self.N is None:
                V = self.M / self.Density
            else:
                # Ideal gas #
                V = self.N * 8.314 * self.Temperature / self.Pressure 
        else:
            V = self.V
        return V

    @property
    def Moles(self):
        if self.N is None:
            if self.V is None:
                N = self.M / self.MolarMass
            else:
                # Ideal gas #
                N = (self.Pressure * self.V) / (8.314 * self.Temperature)
        else:
            N = self.N
        return N

    def Density(self, T=298.15):
        rho = 0
        for i,c in enumerate(self.Components):
            rho += self.MassFractions[i] / c.Density(T)
        return 1 / rho

    def Viscosity(self, T=298.15):
        mu = 1.0
        for i,c in enumerate(self.Components):
            mu = mu*(c.Viscosity(T))**self.MassFractions[i]
        return mu

    def SpecificHeat(self, T=298.15):
        Cp = 0
        for i,c in enumerate(self.Components):
            Cp += self.MassFractions[i] * c.SpecificHeat(T)
        return Cp


class Stream:
    def __init__(self, mixture):
        # Mixture properties #
        self.Components = mixture.Components
        self.ComponentNames = mixture.ComponentNames
        self.Temperature = mixture.Temperature
        self.Pressure = mixture.Pressure
        self.Density = mixture.Density(self.Temperature)
        self.Viscosity = mixture.Viscosity(self.Temperature)
        self.SpecificHeat = mixture.SpecificHeat(self.Temperature)
        self.MolarMass = mixture.MolarMass
        self.MolarMasses = mixture.MolarMasses
        self.MassFractions = mixture.MassFractions
        self.MolarFractions = mixture.MolarFractions
        # Stream properties #
        self.Tag = None
        self.From = None
        self.To = None
        self.Mf = None
        self.Vf = None
        self.Vfo = None
        self.Nf = None
        # Other properties
        self.ParticleSize = None
        self.ParticleCharge = None
        self._To = 273.15
        self._Po = 101325.0
        
    @property
    def MassFlow(self):
        if self.Mf is None:
            if self.Nf is None:
                return self.VolumeFlow * self.Density
            else:
                return self.Nf * self.MolarMass
        else:
            return self.Mf

    @property
    def VolumeFlow(self):
        if self.Vf is None:
            if self.Vfo is None:
                return self.Mf / self.Density
            else:
                return self.NormalVolumeFlow * (self._Po / self._To) * (self.Temperature / self.Pressure)
        else:
            return self.Vf

    @property
    def NormalVolumeFlow(self):
        if self.Vfo is None:
            return self.VolumeFlow * (self._To / self._Po) * (self.Pressure / self.Temperature)
        else:
            return self.Vfo

    @property
    def MolarFlow(self):
        if self.Nf is None:
            return self.MassFlow / self.MolarMass
        else:
            return self.Nf

    @property
    def MassFlows(self):
        return [wi * self.MassFlow for wi in self.MassFractions]

    @property
    def VolumeFlows(self):
        return [zi * self.VolumeFlow for zi in self.MolarFractions]

    @property
    def MolarFlows(self):
        return [zi * self.MolarFlow for zi in self.MolarFractions] 



    @property
    def Velocity(self, diameter):
        return self.VolumeFlow / Circle(diameter).Area