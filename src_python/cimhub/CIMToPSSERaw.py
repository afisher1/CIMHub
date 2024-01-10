from argparse import ArgumentParser
from dataclasses import dataclass
import importlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from cimgraph.databases import ConnectionParameters
from cimgraph.databases.blazegraph.blazegraph import BlazegraphConnection
from cimgraph.databases.graphdb.graphdb import GraphDBConnection
from cimgraph.databases.neo4j.neo4j import Neo4jConnection
from cimgraph.models import FeederModel, BusBranchModel
import cimgraph.utils as cimUtils

@dataclass
class CaseIdentificationData:
    new_case_flag: int = 0
    system_base_mva: float = 100.0
    revision: int = 33
    transformer_ratings_units: int = 0
    branch_ratings_units: int = 0
    system_base_frequency: float = 60.0
    case_title_record_1: str = ''
    case_title_record_2: str = ''


    def toString(self) -> str:
        return f"{self.new_case_flag:d},{self.system_base_mva:.3f},{self.revision:d},{self.transformer_ratings_units:d},{self.branch_ratings_units:d},{self.system_base_frequency:.5f}\n{self.case_title_record_1:59s}\n{self.case_title_record_2:59s}"


    def fromCIM(self, simulationId: str, modelContainerObj: cim.EquipmentContainer, basePowerObj: cim.BasePower = None, baseFrequencyObj: cim.BaseFrequency = None):
        if isinstance(simulationId,str) == False:
            raise TypeError(f"simulationId is not a string type. simulationId type: {type(simulationId)}.")
        if isinstance(modelContainerObj,cim.EquipmentContainer) == False:
            raise TypeError(f"modelContainerObj is not an instance of cim.EquipmentContainer. modelContainerObj type: {type(modelContainerObj)}.")
        if isinstance(basePowerObj,cim.BasePower) == False and basePowerObj is not None:
            raise TypeError(f"basePowerObj is not an instance of cim.BasePower. basePowerObj type: {type(basePowerObj)}.")
        if isinstance(baseFrequencyObj,cim.BaseFrequency) == False and baseFrequencyObj is not None:
            raise TypeError(f"baseFrequencyObj is not an instance of cim.BaseFrequency. baseFrequencyObj type: {type(baseFrequencyObj)}.")
        self.case_title_record_1 = simulationId
        self.case_title_record_2 = modelContainerObj.name
        if basePowerObj is not None:
            self.system_base_mva = basePowerObj.basePower / 1.0e6
        if baseFrequencyObj is not None:
            self.system_base_frequency = baseFrequencyObj.frequency


@dataclass
class BusData:
    bus_number: int
    name: str = ''
    base_voltage: float = 0.0
    bus_type: int = 1
    area: int = 1
    zone: int = 1
    owner: int = 1
    voltage_magnitude: float = 1.0
    voltage_angle: float = 0.0
    normal_voltage_magnitude_high_limit: float = 1.1
    normal_voltage_magnitude_low_limit: float = 0.9
    emergency_voltage_magnitude_high_limit: float = 1.1
    emergency_voltage_magnitude_low_limit: float = 0.9


    def toString(self) -> str:
        return f"{self.bus_number:d},'{self.name:12s}',{self.base_voltage:.4f},{self.bus_type:d},{self.area:d},{self.zone:d},{self.owner:d},{self.voltage_magnitude:.5f},{self.voltage_angle:.4f},{self.normal_voltage_magnitude_high_limit:.5f},{self.normal_voltage_magnitude_low_limit:.5f},{self.emergency_voltage_magnitude_high_limit:.5f},{self.emergency_voltage_magnitude_low_limit:.5f}"
    
    def fromCIM(self, connectivityNodeObj: cim.ConnectivityNode):
        if isinstance(connectivityNodeObj,cim.BasePower) == False:
            raise TypeError(f"connectivityNodeObj is not an instance of cim.ConnectivityNode. connectivityNodeObj type: {type(connectivityNodeObj)}.")
        if connectivityNodeObj.aliasName.isdigit():
            self.bus_number = int(connectivityNodeObj.aliasName)
        else:
            raise ValueError(f"The string contents of connectivityNodeObj.aliasName are not numerical. connectivityNodeObj.aliasName: '{connectivityNodeObj.aliasName:s}'.")
        self.name = connectivityNodeObj.name
        if len(connectivityNodeObj.Terminals) > 0:
            # determine base voltage in kV
            if connectivityNodeObj.Terminals[0].ConductingEquipment is not None:
                if connectivityNodeObj.Terminals[0].ConductingEquipemnt.BaseVoltage is not None:
                    if connectivityNodeObj.Terminals[0].ConductingEquipemnt.BaseVoltage.nominalVoltage is not None:
                        self.base_voltage = connectivityNodeObj.Terminals[0].ConductingEquipemnt.BaseVoltage.nominalVoltage / 1.0e3
                    else:
                        raise ValueError(f"The nominal voltage associated with connectivityNodeObj, {connectivityNodeObj.name}, is None.")
                else:
                    raise ValueError(f"The BaseVoltage object associated with connectivityNodeObj, {connectivityNodeObj.name}, is None.")
            else:
                raise ValueError(f"The ConductingEquipment object associated with connectivityNodeObj, {connectivityNodeObj.name}, is None.")
            # determine bus type
            for terminal in connectivityNodeObj.Terminals:
                if terminal.ConductingEquipment is not None:
                    if isinstance(terminal.ConducingEquipment, cim.EnergySource): # This bus is the swing bus
                        self.bus_type = 3
                        break
                    elif isinstance(terminal.ConductingEquipment, cim.SynchronousMachine):
                        if terminal.ConductingEquipment.operatingMode == cim.SynchronousMachineOperatingMode.generator:
                            self.bus_type = 2
                    elif isinstance(terminal.ConductingEquipment, cim.AsynchronousMachine):
                        if terminal.COnductingEquipment.asynchronousMachineType == cim.AsynchronousMachineKind.generator:
                            self.bus_type = 2
                    elif isinstance(terminal.COnductingEquipment, cim.PowerElectronicsConnection):
                        self.bus_type = 2
        else:
            raise ValueError(f"There are no Terminal objects associated with connectivityNodeObj, {connectivityNodeObj.name}.")
        


        



@dataclass
class LoadData:
    bus_number: int
    load_id: str = '1'
    status: int = 1
    area: int = 1
    zone: int = 1
    constant_real_power: float = 0.0
    constant_imag_power: float = 0.0
    constant_current_real_power: float = 0.0
    constant_current_imag_power: float = 0.0
    constant_admittance_real_power: float = 0.0
    constant_admittance_imag_power: float = 0.0
    owner: int = 1
    scale: int = 1
    interruptible: int = 0

    def toString(self) -> str:
        return f"{self.bus_number:d},'{self.load_id:2s}',{self.status:d},{self.area:d},{self.zone:d},{self.constant_real_power:.3f},{self.constant_imag_power:.3f},{self.constant_current_real_power:.3f},{self.constant_current_imag_power:.3f},{self.constant_admittance_real_power:.3f},{self.constant_admittance_imag_power:.3f},{self.owner:d},{self.scale:d},{self.interruptible:d}"
    
    def fromCIM(self, energyConsumer: cim.EnergyConsumer):
        #TODO figure out which cim object translates to a PSSE load object.
        pass


@dataclass
class FixedShunt:
    bus_number: int
    shunt_id: str = '1'
    status: int = 1
    gl: float = 0.0
    bl: float = 0.0

    def toString(self) -> str:
        return f"{self.bus_number:d},'{self.shunt_id:2s}',{self.status:d},{self.gl:.3f},{self.bl:.3f}"
    
    def fromCIM(self, linearShuntCompensator: cim.LinearShuntCompensator):
        #TODO
        pass


@dataclass
class Generator:
    bus_number: int
    gen_id: str = '1'
    p_output: float = 0.0
    q_output: float
    max_q_output: float = 9999.0
    min_q_output: float = -9999.0
    regulated_voltage_setpoint: float = 1.0
    regulated_bus_number: int = 0
    rated_mva: float
    zr: float = 0.0
    zx: float = 1.0
    rt: float = 0.0
    xt: float = 0.0
    gtap: float = 1.0
    status: int = 1
    rmpct: float = 100.0
    max_p_output: float = 9999.0
    min_p_output: float = -9999.0
    o1: int = 1
    f1: float = 1.0
    o2: int = 0
    f2: float = 1.0
    o3: int = 0
    f3: float = 1.0
    o4: int = 0
    f4: float = 1.0
    wmod: int = 0
    wpf: float = 1.0

    def toString(self) -> str:
        return f"{self.bus_number:d},'{self.gen_id:2s}',{self.p_output:.3f},{self.q_output:.3f},{self.max_q_output:.3f},{self.min_q_output:.3f},{self.regulated_voltage_setpoint:.5f},{self.regulated_bus_number:d},{self.rated_mva:.3f},{self.zr:.5f},{self.zx:.5f},{self.rt:.5f},{self.xt:.5f},{self.gtap:.5f},{self.status:d},{self.rmpct:.1f},{self.max_p_output:.3f},{self.min_p_output:.3f},{self.o1:d},{self.f1:.4f},{self.o2:d},{self.f2:.4f},{self.o3:d},{self.f3:.4f},{self.o4:d},{self.f4:.4f},{self.wmod:d},{self.wpf:.4f}"
    
    def fromCIM(self, cimGeneratorObject: object):
        #TODO
        pass


@dataclass
class Branch:
    from_bus_number: int
    to_bus_number: int
    circuit: str = '1'
    r: float
    x: float
    b: float = 0.0
    rating_1: float = 0.0
    rating_2: float = 0.0
    rating_3: float = 0.0
    g_from: float = 0.0
    b_from: float = 0.0
    g_to: float = 0.0
    b_to: float = 0.0
    status: int = 1
    metered_end: int = 1
    length: float = 0.0
    o1: int = 1
    f1: float = 1.0
    o2: int = 0
    f2: float = 1.0
    o3: int = 0
    f3: float = 1.0
    o4: int = 0
    f4: float = 1.0

    def toString(self) -> str:
        return f"{self.from_bus_number:d},{self.to_bus_number:d},'{self.circuit:2s}',{self.r:.5f},{self.x:.5f},{self.b:.5f},{self.rating_1:.2f},{self.rating_2:.2f},{self.rating_3:.2f},{self.g_from:.5f},{self.b_from:.5f},{self.g_to:.5f},{self.b_to:.5f},{self.status:d},{self.metered_end:d},{self.length:.1f},{self.o1:d},{self.f1:.4f},{self.o2:d},{self.f2:.4f},{self.o3:d},{self.f3:.4f},{self.o4:d},{self.f4:.4f}"
    
    def fromCIM(self, acLineSegment: cim.ACLineSegment):
        #TODO
        pass


@dataclass
class Transformer:
    winding_1_bus: int
    winding_2_bus: int
    winding_3_bus: int = 0
    circuit: str = '1'
    cw: int = 1
    cz: int = 1
    cm: int = 1
    mag1: float = 0.0
    mag2: float = 0.0
    nmetr: int = 2
    name: str = ''
    status: int = 1
    o1: int
    f1: float = 1.0
    o2: int = 0
    f2: float = 1.0
    o3: int = 0
    f3: float = 1.0
    o4: int = 0
    f4: float = 1.0
    vector_group: str = ''
    r12: float = 0.0
    x12: float
    base_mva_12: float
    r23: float = 0.0
    x23: float
    base_mva_23: float
    r31: float = 0.0
    x31: float
    base_mva_31: float
    vmstar: float = 1.0
    anstar: float = 0.0
    windv1: float = 1.0
    nomv1: float = 0.0
    ang1: float = 0.0
    rata1: float = 0.0
    ratb1: float = 0.0
    ratc1: float = 0.0
    cod1: int = 0
    cont1: int = 0
    rma1: float
    rmi1: float
    vma1: float
    vmi1: float
    ntp1: int = 33
    tab1: int = 0
    cr1: float = 0.0
    cx1: float = 0.0
    cnxa1: float = 0.0
    windv2: float = 1.0
    nomv2: float = 0.0
    ang2: float = 0.0
    rata2: float = 0.0
    ratb2: float = 0.0
    ratc2: float = 0.0
    cod2: int = 0
    cont2: int = 0
    rma2: float
    rmi2: float
    vma2: float
    vmi2: float
    ntp2: int = 33
    tab2: int = 0
    cr2: float = 0.0
    cx2: float = 0.0
    cnxa2: float = 0.0
    windv3: float = 1.0
    nomv3: float = 0.0
    ang3: float = 0.0
    rata3: float = 0.0
    ratb3: float = 0.0
    ratc3: float = 0.0
    cod3: int = 0
    cont3: int = 0
    rma3: float
    rmi3: float
    vma3: float
    vmi3: float
    ntp3: int = 33
    tab3: int = 0
    cr3: float = 0.0
    cx3: float = 0.0
    cnxa3: float = 0.0

    def toString(self) -> str:
        # record 1
        rv = f"{self.winding_1_bus:d},{self.winding_2_bus:d},{self.winding_3_bus:d},'{self.circuit:2s}',{self.cw:d},{self.cz:d},{self.cm:d},{self.mag1:.4f},{self.mag2:.4f},{self.nmetr:d},'{self.name:12s}',{self.status:d},{self.o1:d},{self.f1:.4f},{self.o2:d},{self.f2:.4f},{self.o3:d},{self.f3:.4f},{self.o4:d},{self.f4:.4f},'{self.vector_group:12s}'"
        # record 2
        rv += f"\n{self.r12:.4f},{self.x12:.4f},{self.base_mva_12:.4f}"
        if self.winding_3_bus != 0:
            rv += f",{self.r23:.4f},{self.x23:.4f},{self.base_mva_23:.4f},{self.r31:.4f},{self.x31:.4f},{self.base_mva_31:.4f},{self.vmstar:.4f},{self.anstar:.4f}"
        # record 3
        rv += f"\n{self.windv1:.4f},{self.nomv1:.4f},{self.ang1:.4f},{self.rata1:.4f},{self.ratb1:.4f},{self.ratc1:.4f},{self.cod1:d}"
        if isinstance(self.cont1, int):
            rv += f",{self.cont1:d}"
        else:
            rv += f",'{self.cont1:s}'"
        rv += f",{self.rma1:.4f},{self.rmi1:.4f},{self.vma1:.4f},{self.vmi1:.4f},{self.ntp1:d},{self.tab1:d},{self.cr1:.4f},{self.cx1:.4f},{self.cnxa1:.4f}"
        # record 4
        rv += f"\n{self.windv2:.4f},{self.nomv2:.4f}"
        if self.winding_3_bus != 0:
            rv += f",{self.ang2:.4f},{self.rata2:.4f},{self.ratb2:.4f},{self.ratc2:.4f},{self.cod2:d}"
            if isinstance(self.cont2, int):
                rv += f",{self.cont2:d}"
            else:
                rv += f",'{self.cont2:s}'"
            rv += f",{self.rma2:.4f},{self.rmi2:.4f},{self.vma2:.4f},{self.vmi2:.4f},{self.ntp2:d},{self.tab2:d},{self.cr2:.4f},{self.cx2:.4f},{self.cnxa2:.4f}"
        # record 5
        if self.winding_3_bus != 0:
            rv += f"\n{self.windv2:.4f},{self.nomv2:.4f},{self.ang2:.4f},{self.rata2:.4f},{self.ratb2:.4f},{self.ratc2:.4f},{self.cod2:d}"
            if isinstance(self.cont2, int):
                rv += f",{self.cont2:d}"
            else:
                rv += f",'{self.cont2:s}'"
            rv += f",{self.rma2:.4f},{self.rmi2:.4f},{self.vma2:.4f},{self.vmi2:.4f},{self.ntp2:d},{self.tab2:d},{self.cr2:.4f},{self.cx2:.4f},{self.cnxa2:.4f}"
        return rv
    
    def fromCIM(self, cimPowerTransformer: cim.PowerTransformer):
        #TODO
        pass


@dataclass
class AreaInterchange:
    area_number: int
    bus_number: int = 0
    pdes: float = 0.0
    ptol: float = 10.0
    name: str = ''

    def toString(self) -> str:
        return f"{self.area_number:d},{self.bus_number:d},{self.pdes:.4f},{self.ptol:.4f},'{self.name:12s}'"
    
    def fromCIM(self, cimAreaObject: object):
        #TODO
        pass


@dataclass
class TwoTerminalDCTransmissionLine:
    name: str
    control_mode: int = 0
    rdc: float
    setvl: float
    vschd: float
    vcmod: float = 0.0
    rcomp: float = 0.0
    delti: float = 0.0
    meter: str = 'I'
    dvcmin: float = 0.0
    cccitmx: int = 20
    cccacc: float = 1.0
    ipr: int
    nbr: int
    anmxr: float
    anmnr: float
    rcr: float
    xcr: float
    ebasr: float
    trr: float = 1.0
    tapr: float = 1.0
    tmxr: float = 1.5
    tmnr: float = 0.51
    stpr: float = 0.00625
    icr: int = 0
    ifr: int = 0
    itr: int = 0
    idr: str = '1'
    xcapr: float = 0.0
    ipi: int
    nbi: int
    gammx: float
    gammn: float
    rci: float
    xci: float
    ebasi: float
    tri: float = 1.0
    tapi: float = 1.0
    tmxi: float = 1.5
    tmni: float = 0.51
    stpi: float = 0.00625
    ici: int = 0
    ifi: int = 0
    iti: int = 0
    idi: str = '1'
    xcapi: float = 0.0

    def toString(self) -> str:
        # record 1
        rv = f"'{self.name:12s}',{self.control_mode:d},{self.rdc:.4f},{self.setvl:.4f},{self.vschd:.4f},{self.vcmod:.4f},{self.rcomp:.4f},{self.delti:.4f},'{self.meter:s}',{self.dvcmin:.4f},{self.cccitmx:d},{self.cccacc:.4f}"
        # record 2
        rv += f"\n{self.ipr:d},{self.nbr:d},{self.anmxr:.4f},{self.anmnr:.4f},{self.rcr:.4f},{self.xcr:.4f},{self.ebasr:.4f},{self.trr:.4f},{self.tapr:.4f},{self.tmxr:.4f},{self.tmnr:.4f},{self.stpr:.5f},{self.icr:d},{self.ifr:d},{self.itr:d},'{self.idr:s}',{self.xcapr:.4f}"
        # record 3
        rv += f"\n{self.ipi:d},{self.nbi:d},{self.gammx:.4f},{self.gammn:.4f},{self.rci:.4f},{self.xci:.4f},{self.ebasi:.4f},{self.tri:.4f},{self.tapi:.4f},{self.tmxi:.4f},{self.tmni:.4f},{self.stpi:.5f},{self.ici:d},{self.ifi:d},{self.iti:d},'{self.idi:s}',{self.xcapi:.4f}"
        return rv
    
    def fromCIM(self, twoTerminalDCTransmissionLineObject: object):
        #TODO
        pass


@dataclass
class VoltageSourceConverterDCTransmissionLine:
    name: str
    control_mode: int = 1
    rdc: float
    o1: int = 1
    f1: float = 1.0
    o2: int = 0
    f2: float = 1.0
    o3: int = 0
    f3: float = 1.0
    o4: int = 0
    f4: float = 1.0
    converter_bus1: int
    type1: int
    mode1: int = 1
    dcset1: float
    acset1: float = 1.0
    aloss1: float = 0.0
    bloss1: float = 0.0
    minloss1: float = 0.0
    smax1: float = 0.0
    imax1: float = 0.0
    pwf1: float = 1.0
    maxq1: float = 9999.0
    minq1: float = -9999.0
    remot1: int = 0
    rmpct1: float = 100.0
    converter_bus2: int
    type2: int
    mode2: int = 1
    dcset2: float
    acset2: float = 1.0
    aloss2: float = 0.0
    bloss2: float = 0.0
    minloss2: float = 0.0
    smax2: float = 0.0
    imax2: float = 0.0
    pwf2: float = 1.0
    maxq2: float = 9999.0
    minq2: float = -9999.0
    remot2: int = 0
    rmpct2: float = 100.0

    def toString(self) -> str:
        # record 1
        rv = f"'{self.name:12s}',{self.mdc:d},{self.rdc:.4f},{self.o1:d},{self.f1:.4f},{self.o2:d},{self.f2:.4f},{self.o3:d},{self.f3:.4f},,{self.o4:d},{self.f4:.4f}"
        # record 2
        rv += f"\n{self.converter_bus1:d},{self.type1:d},{self.mode1:d},{self.dcset1:.4f},{self.acset1:.4f},{self.aloss1:.4f},{self.bloss1:.4f},{self.minloss1:.4f},{self.smax1:.4f},{self.imax1:.4f},{self.pwf1:.4f},{self.maxq1:.4f},{self.minq1:.4f},{self.remot1:d},{self.rmpct1:.4f}"
        # record 3
        rv += f"\n{self.converter_bus2:d},{self.type2:d},{self.mode2:d},{self.dcset2:.4f},{self.acset2:.4f},{self.aloss2:.4f},{self.bloss2:.4f},{self.minloss2:.4f},{self.smax2:.4f},{self.imax2:.4f},{self.pwf2:.4f},{self.maxq2:.4f},{self.minq2:.4f},{self.remot2:d},{self.rmpct2:.4f}"
        return rv
    
    def fromCIM(self, voltageSourceConverterDCTransmissionLine: object):
        #TODO
        pass


@dataclass
class TransformerImpedanceCorrectionRecord:
    impedance_correction_num: int
    ti: List[float] = []
    fi: List[float] = []

    def toString(self) -> str:
        rv = f"{self.impedance_correction_num:d}"
        for i in range(len(self.ti)):
            rv += f",{self.ti[i]:.4f},{self.fi[i]:.4f}"
        return rv
    
    def fromCIM(self, cimAreaObject: object):
        #TODO
        pass


@dataclass
class ConverterRecord:
    ib: int
    n: int
    angmx: float
    angmn: float
    rc: float
    xc: float
    ebas: float
    tr: float = 1.0
    tap: float = 1.0
    tpmx: float = 1.5
    tpmn: float = 0.51
    tstp: float = 0.00625
    setvl: float
    dcpf: float = 1.0
    marg: float = 0.0
    cnvcod: int = 1

    def toString(self) -> str:
        return f"{self.ib:d},{self.n:d},{self.angmx:.5f},{self.angmn:.5f},{self.rc:.5f},{self.xc:.5f},{self.ebas:.5f},{self.tr:.5f},{self.tap:.5f},{self.tpmx:.5f},{self.tpmn:.5f},{self.tstp:.5f},{self.setvl:.5f},{self.dcpf:.5f},{self.marg:.5f},{self.cnvcod:d}"
    
    def fromCIM(self, converterRecordObject: object):
        #TODO
        pass


@dataclass
class DCBusRecord:
    idc: int
    ib: int = 0
    area: int = 1
    zone: int = 1
    dcname: str = ''
    idc2: int = 0
    rgrnd: float = 0.0
    owner: int = 1

    def toString(self) -> str:
        return f"{self.idc:d},{self.ib:d},{self.area:d},{self.zone:d},'{self.dcname:12s}',{self.idc2:d},{self.rgrnd:.5f},{self.owner:d}"
    
    def fromCIM(self, dcBusRecordObject: object):
        #TODO
        pass


@dataclass
class DCLinkRecord:
    idc: int
    jdc: int
    dcckt: str = '1'
    met: int = 1
    rdc: float
    ldc: float = 0.0

    def toString(self) -> str:
        return f"{self.idc:d},{self.jdc:d},'{self.dcckt:s}',{self.met:d},{self.rdc:.5f},{self.ldc:.5f}"
    
    def fromCIM(self, dcLinkRecordObject: object):
        #TODO
        pass


@dataclass
class MultiTerminalDCTransmissionLine:
    name: str
    nconv: int
    ndcbs: int
    ndcln: int
    mdc: int = 0
    vconv: int
    vcmod: float = 0.0
    vconvn: int = 0
    converter_records: List[ConverterRecord] = []
    dc_bus_records: List[DCBusRecord] = []
    dc_link_records: List[DCLinkRecord] = []

    def toString(self) -> str:
        rv = f"'{self.name:12s}',{self.nconv:d},{self.ndcbs:d},{self.ndcln:d},{self.mdc:d},{self.vconv:d},{self.vcmod:.4f},{self.vconvn:d}"
        for i in range(self.nconv):
            rv += "\n" + self.converter_records[i].toString()
        for i in range(self.ndcbs):
            rv += "\n" + self.dc_bus_records[i].toString()
        for i in range(self.ndcln):
            rv += "\n" + self.dc_link_records[i].toString()
        return rv
    
    def fromCIM(self, cimAreaObject: object):
        #TODO
        pass


@dataclass
class MultiSectionLine:
    ibus: int
    jbus: int
    line_id: str = '&1'
    met: int = 1
    dumi: List[str] = []
    ldc: float = 0.0

    def toString(self) -> str:
        rv = f"{self.ibus:d},{self.jbus:d},{self.line_id:2s},{self.met:d}"
        for bus in self.dumi:
            rv += f",{bus}"
        return rv
    
    def fromCIM(self, multiSectionLineObject: object):
        #TODO
        pass


@dataclass
class Zone:
    zone_number: int
    name: str = ''

    def toString(self) -> str:
        return f"{self.zone_number:d},'{self.name:12s}'"
    
    def fromCIM(self, zoneObject: object):
        #TODO
        pass


@dataclass
class InterareaTransfer:
    from_area: int
    to_area: int
    transfer_id: str = '1'
    power_transfer: float = 0.0

    def toString(self) -> str:
        return f"{self.from_area:d},{self.to_area:d},{self.transfer_id:s},{self.power_transfer:.4f}"
    
    def fromCIM(self, transferObject: object):
        #TODO
        pass


@dataclass
class Owner:
    owner_number: int
    name: str = ''

    def toString(self) -> str:
        return f"{self.owner_number:d},'{self.name:12s}'"
    
    def fromCIM(self, ownerObject: object):
        #TODO
        pass


@dataclass
class FactsDevice:
    name: str
    ibus: int
    jbus: int = 0
    mode: int = 1
    pdes: float = 0.0
    qdes: float = 0.0
    vset: float = 1.0
    shmx: float = 9999.0
    trmx: float = 9999.0
    vtmn: float = 0.9
    vtmx: float = 1.1
    vsmx: float = 1.0
    imx: float = 0.0
    linx: float = 0.05
    rmpct: float = 100.0
    owner: int = 1
    set1: float = 0.0
    set2: float = 0.0
    vsref: int = 0
    remot: int = 0
    mname: str = ''

    def toString(self) -> str:
        return f"'{self.name:s}',{self.ibus:d},{self.jbus:d},{self.mode:d},{self.pdes:.4f},{self.qdes:.4f},{self.vset:.4f},{self.shmx:.4f},{self.trmx:.4f},{self.vtmn:.4f},{self.vtmx:.4f},{self.vsmx:.4f},{self.imx:.4f},{self.linx:.4f},{self.rmpct:.4f},{self.owner:d},{self.set1:.4f},{self.set2:.4f},{self.vsref:d},{self.remot:d},'{self.mname:s}'"
    
    def fromCIM(self, factsDeviceObject: object):
        #TODO
        pass


@dataclass
class SwitchedShunt:
    bus_number: int
    modsw: int = 1
    adjm: int = 0
    status: int = 1
    vswhi: float = 1.0
    vswlo: float = 1.0
    swrem: int = 0
    rmpct: float = 100.0
    rmidnt: str = ''
    binit: float = 0.0
    ni: List[int] = []
    bi: List[float] = []

    def toString(self) -> str:
        rv = f"{self.bus_number:d},{self.modsw:d},{self.adjm:d},{self.status:d},{self.vswhi:.5f},{self.vswlo:.5f},{self.swrem:d},{self.rmpct:.5f},'{self.rmidnt:s}',{self.binit:.5f}"
        for i in range(len(self.ni)):
            rv += f",{self.ni[i]:d},{self.bi[i]:.5f}"
        if len(self.ni) < 9:
            rv += f",0,0.00000"
        return rv
    
    def fromCIM(self, switchedShuntObject: object):
        #TODO
        pass


@dataclass
class InductionMachine:
    bus_id: int
    name: str = '1'
    status: int = 1
    scode: int = 1
    dcode: int = 2
    area: int
    zone: int
    owner: int
    tcode: int = 1
    bcode: int = 1
    mbase: float
    ratekv: float = 0.0
    pcode: int = 1
    pset: float
    h: float = 1.0
    a: float = 1.0
    b: float = 1.0
    d: float = 1.0
    e: float = 1.0
    ra: float = 0.0
    xa: float = 0.0
    r1: float = 999.0
    x1: float = 999.0
    r2: float = 999.0
    x2: float = 999.0
    x3: float = 0.0
    e1: float = 1.0
    se1: float = 0.0
    e2: float = 1.2
    se2: float = 0.0
    ia1: float = 0.0
    ia2: float = 0.0
    xamult: float = 1.0

    def toString(self) -> str:
        return f"{self.bus_id:d},'{self.name:s}',{self.status:d},{self.scode:d},{self.dcode:d},{self.area:d},{self.zone:d},{self.owner:d},{self.tcode:d},{self.bcode:d},{self.mbase:.4f},{self.ratekv:.4f},{self.pcode:d},{self.pset:.4f},{self.h:.4f},{self.a:.4f},{self.b:.4f},{self.d:.4f},{self.e:.4f},{self.ra:.4f},{self.xa:.4f},{self.r1:.4f},{self.x1:.4f},{self.r2:.4f},{self.x2:.4f},{self.x3:.4f},{self.e1:.4f},{self.se1:.4f},{self.e2:.4f},{self.se2:.4f},{self.ia1:.4f},{self.ia2:.4f},{self.xamult:.4f}"
    
    def fromCIM(self, inductionMachineObject: object):
        #TODO
        pass


@dataclass
class SwitchedShunt:
    bus_number: int
    modsw: int = 1
    adjm: int = 0
    status: int = 1
    vswhi: float = 1.0
    vswlo: float = 1.0
    swrem: int = 0
    rmpct: float = 100.0
    rmidnt: str = ''
    binit: float = 0.0
    ni: List[int] = []
    bi: List[float] = []

    def toString(self) -> str:
        rv = f"{self.bus_number:d},{self.modsw:d},{self.adjm:d},{self.status:d},{self.vswhi:.5f},{self.vswlo:.5f},{self.swrem:d},{self.rmpct:.5f},'{self.rmidnt:s}',{self.binit:.5f}"
        for i in range(len(self.ni)):
            rv += f",{self.ni[i]:d},{self.bi[i]:.5f}"
        if len(self.ni) < 9:
            rv += f",0,0.00000"
        return rv
    
    def fromCIM(self, switchedShuntObject: object):
        #TODO
        pass

    

def createDatabaseConnection(db_type: str, db_url: str, cim_profile: str) -> object:
        db_connection = None
        if db_type not in ["Blazegraph", "GraphDB", "Neo4j"]:
            raise RuntimeError(f"Unsupported database type, {db_type}, specified! Current supported databases are: Blazegraph, GraphDB, and Neo4j")
        if db_type == "Blazegraph":
            params = ConnectionParameters(url = db_url, cim_profile = cim_profile)
            db_connection = BlazegraphConnection(params)
        elif db_type == "GraphDB":
            params = ConnectionParameters(url = db_url, cim_profile = cim_profile)
            db_connection = GraphDBConnection(params)
        elif db_type == "Neo4j":
            params = ConnectionParameters(url = db_url, cim_profile = cim_profile)
            db_connection = Neo4jConnection(params)
        return db_connection


def cimToPsseRaw(database: str, database_url: str, cim_profile: str, system_model_mrid: str, output_file_path: Path):
    """Converts CIM busBranch model to PSSE Raw file.
        Args:
            database: The CIM database type to connect to. 
                Type: str.
                Valid Entries: Blazegraph, GraphDB, Neo4j.
            database_url: The url of lthe database to connect to.
                Type: str.
            cim_profile: The CIM propfile to use.
                Type: str.
            system_model_mrid: The busBranch model MRID to convert.
                Type: str.
            output_file_path: The full output file path.
                Type: pathlib.Path
        Returns: None
    """
    global cim
    cim = importlib.import_module(f"cimgraph.data_profile.{cim_profile}")
    db_connection = createDatabaseConnection(database, database_url)
    bus_branch_container = cim.ConnectivityNodeContainer(mRID=system_model_mrid)
    graph_model = BusBranchModel(connection=db_connection, container=bus_branch_container, distributed=False)
    cimUtils.get_all_data(graph_model)
    psse_data = {}
    with open(output_file_path, 'w') as psse_fh:
         pass
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("database", help="The database type to connect to: Blazegraph, GraphDB, or Neo4j.")
    parser.add_argument("database_url", help="The url of the database to connect to.")
    parser.add_argument("cim_profile", help="The cim profile to use.")
    parser.add_argument("system_model_mrid", help="The system model to edit.")
    parser.add_argument("output_file_path", help="The full file output path.")
    args = parser.parse_args()
    cimToPsseRaw(args.database, args.database_url, args.cim_profile, args.system_model_mrid,Path(args.output_file_path))