# mypy: ignore-errors
# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes, os


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



_libraries = {}
_libraries['libpciaccess.so'] = ctypes.CDLL('/usr/lib/x86_64-linux-gnu/libpciaccess.so') if os.path.exists('/usr/lib/x86_64-linux-gnu/libpciaccess.so') else None
c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))





PCIACCESS_H = True # macro
# __deprecated = ((deprecated)) # macro
PCI_DEV_MAP_FLAG_WRITABLE = (1<<0) # macro
PCI_DEV_MAP_FLAG_WRITE_COMBINE = (1<<1) # macro
PCI_DEV_MAP_FLAG_CACHABLE = (1<<2) # macro
PCI_MATCH_ANY = (~0) # macro
def PCI_ID_COMPARE(a, b):  # macro
   return (((a)==(~0)) or ((a)==(b)))
VGA_ARB_RSRC_NONE = 0x00 # macro
VGA_ARB_RSRC_LEGACY_IO = 0x01 # macro
VGA_ARB_RSRC_LEGACY_MEM = 0x02 # macro
VGA_ARB_RSRC_NORMAL_IO = 0x04 # macro
VGA_ARB_RSRC_NORMAL_MEM = 0x08 # macro
pciaddr_t = ctypes.c_uint64
class struct_pci_device_iterator(Structure):
    pass

class struct_pci_device(Structure):
    pass

try:
    pci_device_has_kernel_driver = _libraries['libpciaccess.so'].pci_device_has_kernel_driver
    pci_device_has_kernel_driver.restype = ctypes.c_int32
    pci_device_has_kernel_driver.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_is_boot_vga = _libraries['libpciaccess.so'].pci_device_is_boot_vga
    pci_device_is_boot_vga.restype = ctypes.c_int32
    pci_device_is_boot_vga.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_read_rom = _libraries['libpciaccess.so'].pci_device_read_rom
    pci_device_read_rom.restype = ctypes.c_int32
    pci_device_read_rom.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    pci_device_map_region = _libraries['libpciaccess.so'].pci_device_map_region
    pci_device_map_region.restype = ctypes.c_int32
    pci_device_map_region.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.c_uint32, ctypes.c_int32]
except AttributeError:
    pass
try:
    pci_device_unmap_region = _libraries['libpciaccess.so'].pci_device_unmap_region
    pci_device_unmap_region.restype = ctypes.c_int32
    pci_device_unmap_region.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.c_uint32]
except AttributeError:
    pass
try:
    pci_device_map_range = _libraries['libpciaccess.so'].pci_device_map_range
    pci_device_map_range.restype = ctypes.c_int32
    pci_device_map_range.argtypes = [ctypes.POINTER(struct_pci_device), pciaddr_t, pciaddr_t, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    pci_device_unmap_range = _libraries['libpciaccess.so'].pci_device_unmap_range
    pci_device_unmap_range.restype = ctypes.c_int32
    pci_device_unmap_range.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None), pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_map_memory_range = _libraries['libpciaccess.so'].pci_device_map_memory_range
    pci_device_map_memory_range.restype = ctypes.c_int32
    pci_device_map_memory_range.argtypes = [ctypes.POINTER(struct_pci_device), pciaddr_t, pciaddr_t, ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    pci_device_unmap_memory_range = _libraries['libpciaccess.so'].pci_device_unmap_memory_range
    pci_device_unmap_memory_range.restype = ctypes.c_int32
    pci_device_unmap_memory_range.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None), pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_probe = _libraries['libpciaccess.so'].pci_device_probe
    pci_device_probe.restype = ctypes.c_int32
    pci_device_probe.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
class struct_pci_agp_info(Structure):
    pass

try:
    pci_device_get_agp_info = _libraries['libpciaccess.so'].pci_device_get_agp_info
    pci_device_get_agp_info.restype = ctypes.POINTER(struct_pci_agp_info)
    pci_device_get_agp_info.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
class struct_pci_bridge_info(Structure):
    pass

try:
    pci_device_get_bridge_info = _libraries['libpciaccess.so'].pci_device_get_bridge_info
    pci_device_get_bridge_info.restype = ctypes.POINTER(struct_pci_bridge_info)
    pci_device_get_bridge_info.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
class struct_pci_pcmcia_bridge_info(Structure):
    pass

try:
    pci_device_get_pcmcia_bridge_info = _libraries['libpciaccess.so'].pci_device_get_pcmcia_bridge_info
    pci_device_get_pcmcia_bridge_info.restype = ctypes.POINTER(struct_pci_pcmcia_bridge_info)
    pci_device_get_pcmcia_bridge_info.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_get_bridge_buses = _libraries['libpciaccess.so'].pci_device_get_bridge_buses
    pci_device_get_bridge_buses.restype = ctypes.c_int32
    pci_device_get_bridge_buses.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    pci_system_init = _libraries['libpciaccess.so'].pci_system_init
    pci_system_init.restype = ctypes.c_int32
    pci_system_init.argtypes = []
except AttributeError:
    pass
try:
    pci_system_init_dev_mem = _libraries['libpciaccess.so'].pci_system_init_dev_mem
    pci_system_init_dev_mem.restype = None
    pci_system_init_dev_mem.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    pci_system_cleanup = _libraries['libpciaccess.so'].pci_system_cleanup
    pci_system_cleanup.restype = None
    pci_system_cleanup.argtypes = []
except AttributeError:
    pass
class struct_pci_slot_match(Structure):
    pass

try:
    pci_slot_match_iterator_create = _libraries['libpciaccess.so'].pci_slot_match_iterator_create
    pci_slot_match_iterator_create.restype = ctypes.POINTER(struct_pci_device_iterator)
    pci_slot_match_iterator_create.argtypes = [ctypes.POINTER(struct_pci_slot_match)]
except AttributeError:
    pass
class struct_pci_id_match(Structure):
    pass

try:
    pci_id_match_iterator_create = _libraries['libpciaccess.so'].pci_id_match_iterator_create
    pci_id_match_iterator_create.restype = ctypes.POINTER(struct_pci_device_iterator)
    pci_id_match_iterator_create.argtypes = [ctypes.POINTER(struct_pci_id_match)]
except AttributeError:
    pass
try:
    pci_iterator_destroy = _libraries['libpciaccess.so'].pci_iterator_destroy
    pci_iterator_destroy.restype = None
    pci_iterator_destroy.argtypes = [ctypes.POINTER(struct_pci_device_iterator)]
except AttributeError:
    pass
try:
    pci_device_next = _libraries['libpciaccess.so'].pci_device_next
    pci_device_next.restype = ctypes.POINTER(struct_pci_device)
    pci_device_next.argtypes = [ctypes.POINTER(struct_pci_device_iterator)]
except AttributeError:
    pass
uint32_t = ctypes.c_uint32
try:
    pci_device_find_by_slot = _libraries['libpciaccess.so'].pci_device_find_by_slot
    pci_device_find_by_slot.restype = ctypes.POINTER(struct_pci_device)
    pci_device_find_by_slot.argtypes = [uint32_t, uint32_t, uint32_t, uint32_t]
except AttributeError:
    pass
try:
    pci_device_get_parent_bridge = _libraries['libpciaccess.so'].pci_device_get_parent_bridge
    pci_device_get_parent_bridge.restype = ctypes.POINTER(struct_pci_device)
    pci_device_get_parent_bridge.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_get_strings = _libraries['libpciaccess.so'].pci_get_strings
    pci_get_strings.restype = None
    pci_get_strings.argtypes = [ctypes.POINTER(struct_pci_id_match), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
except AttributeError:
    pass
try:
    pci_device_get_device_name = _libraries['libpciaccess.so'].pci_device_get_device_name
    pci_device_get_device_name.restype = ctypes.POINTER(ctypes.c_char)
    pci_device_get_device_name.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_get_subdevice_name = _libraries['libpciaccess.so'].pci_device_get_subdevice_name
    pci_device_get_subdevice_name.restype = ctypes.POINTER(ctypes.c_char)
    pci_device_get_subdevice_name.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_get_vendor_name = _libraries['libpciaccess.so'].pci_device_get_vendor_name
    pci_device_get_vendor_name.restype = ctypes.POINTER(ctypes.c_char)
    pci_device_get_vendor_name.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_get_subvendor_name = _libraries['libpciaccess.so'].pci_device_get_subvendor_name
    pci_device_get_subvendor_name.restype = ctypes.POINTER(ctypes.c_char)
    pci_device_get_subvendor_name.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_enable = _libraries['libpciaccess.so'].pci_device_enable
    pci_device_enable.restype = None
    pci_device_enable.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_cfg_read = _libraries['libpciaccess.so'].pci_device_cfg_read
    pci_device_cfg_read.restype = ctypes.c_int32
    pci_device_cfg_read.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None), pciaddr_t, pciaddr_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    pci_device_cfg_read_u8 = _libraries['libpciaccess.so'].pci_device_cfg_read_u8
    pci_device_cfg_read_u8.restype = ctypes.c_int32
    pci_device_cfg_read_u8.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(ctypes.c_ubyte), pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_cfg_read_u16 = _libraries['libpciaccess.so'].pci_device_cfg_read_u16
    pci_device_cfg_read_u16.restype = ctypes.c_int32
    pci_device_cfg_read_u16.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(ctypes.c_uint16), pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_cfg_read_u32 = _libraries['libpciaccess.so'].pci_device_cfg_read_u32
    pci_device_cfg_read_u32.restype = ctypes.c_int32
    pci_device_cfg_read_u32.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(ctypes.c_uint32), pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_cfg_write = _libraries['libpciaccess.so'].pci_device_cfg_write
    pci_device_cfg_write.restype = ctypes.c_int32
    pci_device_cfg_write.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None), pciaddr_t, pciaddr_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
uint8_t = ctypes.c_uint8
try:
    pci_device_cfg_write_u8 = _libraries['libpciaccess.so'].pci_device_cfg_write_u8
    pci_device_cfg_write_u8.restype = ctypes.c_int32
    pci_device_cfg_write_u8.argtypes = [ctypes.POINTER(struct_pci_device), uint8_t, pciaddr_t]
except AttributeError:
    pass
uint16_t = ctypes.c_uint16
try:
    pci_device_cfg_write_u16 = _libraries['libpciaccess.so'].pci_device_cfg_write_u16
    pci_device_cfg_write_u16.restype = ctypes.c_int32
    pci_device_cfg_write_u16.argtypes = [ctypes.POINTER(struct_pci_device), uint16_t, pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_cfg_write_u32 = _libraries['libpciaccess.so'].pci_device_cfg_write_u32
    pci_device_cfg_write_u32.restype = ctypes.c_int32
    pci_device_cfg_write_u32.argtypes = [ctypes.POINTER(struct_pci_device), uint32_t, pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_cfg_write_bits = _libraries['libpciaccess.so'].pci_device_cfg_write_bits
    pci_device_cfg_write_bits.restype = ctypes.c_int32
    pci_device_cfg_write_bits.argtypes = [ctypes.POINTER(struct_pci_device), uint32_t, uint32_t, pciaddr_t]
except AttributeError:
    pass
class struct_pci_mem_region(Structure):
    pass

struct_pci_mem_region._pack_ = 1 # source:False
struct_pci_mem_region._fields_ = [
    ('memory', ctypes.POINTER(None)),
    ('bus_addr', ctypes.c_uint64),
    ('base_addr', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
    ('is_IO', ctypes.c_uint32, 1),
    ('is_prefetchable', ctypes.c_uint32, 1),
    ('is_64', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint64, 61),
]

class struct_pci_pcmcia_bridge_info_0(Structure):
    pass

struct_pci_pcmcia_bridge_info_0._pack_ = 1 # source:False
struct_pci_pcmcia_bridge_info_0._fields_ = [
    ('base', ctypes.c_uint32),
    ('limit', ctypes.c_uint32),
]

class struct_pci_pcmcia_bridge_info_1(Structure):
    pass

struct_pci_pcmcia_bridge_info_1._pack_ = 1 # source:False
struct_pci_pcmcia_bridge_info_1._fields_ = [
    ('base', ctypes.c_uint32),
    ('limit', ctypes.c_uint32),
]

try:
    pci_device_vgaarb_init = _libraries['libpciaccess.so'].pci_device_vgaarb_init
    pci_device_vgaarb_init.restype = ctypes.c_int32
    pci_device_vgaarb_init.argtypes = []
except AttributeError:
    pass
try:
    pci_device_vgaarb_fini = _libraries['libpciaccess.so'].pci_device_vgaarb_fini
    pci_device_vgaarb_fini.restype = None
    pci_device_vgaarb_fini.argtypes = []
except AttributeError:
    pass
try:
    pci_device_vgaarb_set_target = _libraries['libpciaccess.so'].pci_device_vgaarb_set_target
    pci_device_vgaarb_set_target.restype = ctypes.c_int32
    pci_device_vgaarb_set_target.argtypes = [ctypes.POINTER(struct_pci_device)]
except AttributeError:
    pass
try:
    pci_device_vgaarb_decodes = _libraries['libpciaccess.so'].pci_device_vgaarb_decodes
    pci_device_vgaarb_decodes.restype = ctypes.c_int32
    pci_device_vgaarb_decodes.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    pci_device_vgaarb_lock = _libraries['libpciaccess.so'].pci_device_vgaarb_lock
    pci_device_vgaarb_lock.restype = ctypes.c_int32
    pci_device_vgaarb_lock.argtypes = []
except AttributeError:
    pass
try:
    pci_device_vgaarb_trylock = _libraries['libpciaccess.so'].pci_device_vgaarb_trylock
    pci_device_vgaarb_trylock.restype = ctypes.c_int32
    pci_device_vgaarb_trylock.argtypes = []
except AttributeError:
    pass
try:
    pci_device_vgaarb_unlock = _libraries['libpciaccess.so'].pci_device_vgaarb_unlock
    pci_device_vgaarb_unlock.restype = ctypes.c_int32
    pci_device_vgaarb_unlock.argtypes = []
except AttributeError:
    pass
try:
    pci_device_vgaarb_get_info = _libraries['libpciaccess.so'].pci_device_vgaarb_get_info
    pci_device_vgaarb_get_info.restype = ctypes.c_int32
    pci_device_vgaarb_get_info.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
class struct_pci_io_handle(Structure):
    pass

try:
    pci_device_open_io = _libraries['libpciaccess.so'].pci_device_open_io
    pci_device_open_io.restype = ctypes.POINTER(struct_pci_io_handle)
    pci_device_open_io.argtypes = [ctypes.POINTER(struct_pci_device), pciaddr_t, pciaddr_t]
except AttributeError:
    pass
try:
    pci_legacy_open_io = _libraries['libpciaccess.so'].pci_legacy_open_io
    pci_legacy_open_io.restype = ctypes.POINTER(struct_pci_io_handle)
    pci_legacy_open_io.argtypes = [ctypes.POINTER(struct_pci_device), pciaddr_t, pciaddr_t]
except AttributeError:
    pass
try:
    pci_device_close_io = _libraries['libpciaccess.so'].pci_device_close_io
    pci_device_close_io.restype = None
    pci_device_close_io.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(struct_pci_io_handle)]
except AttributeError:
    pass
try:
    pci_io_read32 = _libraries['libpciaccess.so'].pci_io_read32
    pci_io_read32.restype = uint32_t
    pci_io_read32.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t]
except AttributeError:
    pass
try:
    pci_io_read16 = _libraries['libpciaccess.so'].pci_io_read16
    pci_io_read16.restype = uint16_t
    pci_io_read16.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t]
except AttributeError:
    pass
try:
    pci_io_read8 = _libraries['libpciaccess.so'].pci_io_read8
    pci_io_read8.restype = uint8_t
    pci_io_read8.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t]
except AttributeError:
    pass
try:
    pci_io_write32 = _libraries['libpciaccess.so'].pci_io_write32
    pci_io_write32.restype = None
    pci_io_write32.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t, uint32_t]
except AttributeError:
    pass
try:
    pci_io_write16 = _libraries['libpciaccess.so'].pci_io_write16
    pci_io_write16.restype = None
    pci_io_write16.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t, uint16_t]
except AttributeError:
    pass
try:
    pci_io_write8 = _libraries['libpciaccess.so'].pci_io_write8
    pci_io_write8.restype = None
    pci_io_write8.argtypes = [ctypes.POINTER(struct_pci_io_handle), uint32_t, uint8_t]
except AttributeError:
    pass
try:
    pci_device_map_legacy = _libraries['libpciaccess.so'].pci_device_map_legacy
    pci_device_map_legacy.restype = ctypes.c_int32
    pci_device_map_legacy.argtypes = [ctypes.POINTER(struct_pci_device), pciaddr_t, pciaddr_t, ctypes.c_uint32, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    pci_device_unmap_legacy = _libraries['libpciaccess.so'].pci_device_unmap_legacy
    pci_device_unmap_legacy.restype = ctypes.c_int32
    pci_device_unmap_legacy.argtypes = [ctypes.POINTER(struct_pci_device), ctypes.POINTER(None), pciaddr_t]
except AttributeError:
    pass
LINUX_PCI_REGS_H = True # macro
PCI_CFG_SPACE_SIZE = 256 # macro
PCI_CFG_SPACE_EXP_SIZE = 4096 # macro
PCI_STD_HEADER_SIZEOF = 64 # macro
PCI_STD_NUM_BARS = 6 # macro
PCI_VENDOR_ID = 0x00 # macro
PCI_DEVICE_ID = 0x02 # macro
PCI_COMMAND = 0x04 # macro
PCI_COMMAND_IO = 0x1 # macro
PCI_COMMAND_MEMORY = 0x2 # macro
PCI_COMMAND_MASTER = 0x4 # macro
PCI_COMMAND_SPECIAL = 0x8 # macro
PCI_COMMAND_INVALIDATE = 0x10 # macro
PCI_COMMAND_VGA_PALETTE = 0x20 # macro
PCI_COMMAND_PARITY = 0x40 # macro
PCI_COMMAND_WAIT = 0x80 # macro
PCI_COMMAND_SERR = 0x100 # macro
PCI_COMMAND_FAST_BACK = 0x200 # macro
PCI_COMMAND_INTX_DISABLE = 0x400 # macro
PCI_STATUS = 0x06 # macro
PCI_STATUS_IMM_READY = 0x01 # macro
PCI_STATUS_INTERRUPT = 0x08 # macro
PCI_STATUS_CAP_LIST = 0x10 # macro
PCI_STATUS_66MHZ = 0x20 # macro
PCI_STATUS_UDF = 0x40 # macro
PCI_STATUS_FAST_BACK = 0x80 # macro
PCI_STATUS_PARITY = 0x100 # macro
PCI_STATUS_DEVSEL_MASK = 0x600 # macro
PCI_STATUS_DEVSEL_FAST = 0x000 # macro
PCI_STATUS_DEVSEL_MEDIUM = 0x200 # macro
PCI_STATUS_DEVSEL_SLOW = 0x400 # macro
PCI_STATUS_SIG_TARGET_ABORT = 0x800 # macro
PCI_STATUS_REC_TARGET_ABORT = 0x1000 # macro
PCI_STATUS_REC_MASTER_ABORT = 0x2000 # macro
PCI_STATUS_SIG_SYSTEM_ERROR = 0x4000 # macro
PCI_STATUS_DETECTED_PARITY = 0x8000 # macro
PCI_CLASS_REVISION = 0x08 # macro
PCI_REVISION_ID = 0x08 # macro
PCI_CLASS_PROG = 0x09 # macro
PCI_CLASS_DEVICE = 0x0a # macro
PCI_CACHE_LINE_SIZE = 0x0c # macro
PCI_LATENCY_TIMER = 0x0d # macro
PCI_HEADER_TYPE = 0x0e # macro
PCI_HEADER_TYPE_MASK = 0x7f # macro
PCI_HEADER_TYPE_NORMAL = 0 # macro
PCI_HEADER_TYPE_BRIDGE = 1 # macro
PCI_HEADER_TYPE_CARDBUS = 2 # macro
PCI_BIST = 0x0f # macro
PCI_BIST_CODE_MASK = 0x0f # macro
PCI_BIST_START = 0x40 # macro
PCI_BIST_CAPABLE = 0x80 # macro
PCI_BASE_ADDRESS_0 = 0x10 # macro
PCI_BASE_ADDRESS_1 = 0x14 # macro
PCI_BASE_ADDRESS_2 = 0x18 # macro
PCI_BASE_ADDRESS_3 = 0x1c # macro
PCI_BASE_ADDRESS_4 = 0x20 # macro
PCI_BASE_ADDRESS_5 = 0x24 # macro
PCI_BASE_ADDRESS_SPACE = 0x01 # macro
PCI_BASE_ADDRESS_SPACE_IO = 0x01 # macro
PCI_BASE_ADDRESS_SPACE_MEMORY = 0x00 # macro
PCI_BASE_ADDRESS_MEM_TYPE_MASK = 0x06 # macro
PCI_BASE_ADDRESS_MEM_TYPE_32 = 0x00 # macro
PCI_BASE_ADDRESS_MEM_TYPE_1M = 0x02 # macro
PCI_BASE_ADDRESS_MEM_TYPE_64 = 0x04 # macro
PCI_BASE_ADDRESS_MEM_PREFETCH = 0x08 # macro
PCI_BASE_ADDRESS_MEM_MASK = (~0x0f) # macro
PCI_BASE_ADDRESS_IO_MASK = (~0x03) # macro
PCI_CARDBUS_CIS = 0x28 # macro
PCI_SUBSYSTEM_VENDOR_ID = 0x2c # macro
PCI_SUBSYSTEM_ID = 0x2e # macro
PCI_ROM_ADDRESS = 0x30 # macro
PCI_ROM_ADDRESS_ENABLE = 0x01 # macro
PCI_ROM_ADDRESS_MASK = (~0x7ff) # macro
PCI_CAPABILITY_LIST = 0x34 # macro
PCI_INTERRUPT_LINE = 0x3c # macro
PCI_INTERRUPT_PIN = 0x3d # macro
PCI_MIN_GNT = 0x3e # macro
PCI_MAX_LAT = 0x3f # macro
PCI_PRIMARY_BUS = 0x18 # macro
PCI_SECONDARY_BUS = 0x19 # macro
PCI_SUBORDINATE_BUS = 0x1a # macro
PCI_SEC_LATENCY_TIMER = 0x1b # macro
PCI_IO_BASE = 0x1c # macro
PCI_IO_LIMIT = 0x1d # macro
PCI_IO_RANGE_TYPE_MASK = 0x0f # macro
PCI_IO_RANGE_TYPE_16 = 0x00 # macro
PCI_IO_RANGE_TYPE_32 = 0x01 # macro
PCI_IO_RANGE_MASK = (~0x0f) # macro
PCI_IO_1K_RANGE_MASK = (~0x03) # macro
PCI_SEC_STATUS = 0x1e # macro
PCI_MEMORY_BASE = 0x20 # macro
PCI_MEMORY_LIMIT = 0x22 # macro
PCI_MEMORY_RANGE_TYPE_MASK = 0x0f # macro
PCI_MEMORY_RANGE_MASK = (~0x0f) # macro
PCI_PREF_MEMORY_BASE = 0x24 # macro
PCI_PREF_MEMORY_LIMIT = 0x26 # macro
PCI_PREF_RANGE_TYPE_MASK = 0x0f # macro
PCI_PREF_RANGE_TYPE_32 = 0x00 # macro
PCI_PREF_RANGE_TYPE_64 = 0x01 # macro
PCI_PREF_RANGE_MASK = (~0x0f) # macro
PCI_PREF_BASE_UPPER32 = 0x28 # macro
PCI_PREF_LIMIT_UPPER32 = 0x2c # macro
PCI_IO_BASE_UPPER16 = 0x30 # macro
PCI_IO_LIMIT_UPPER16 = 0x32 # macro
PCI_ROM_ADDRESS1 = 0x38 # macro
PCI_BRIDGE_CONTROL = 0x3e # macro
PCI_BRIDGE_CTL_PARITY = 0x01 # macro
PCI_BRIDGE_CTL_SERR = 0x02 # macro
PCI_BRIDGE_CTL_ISA = 0x04 # macro
PCI_BRIDGE_CTL_VGA = 0x08 # macro
PCI_BRIDGE_CTL_MASTER_ABORT = 0x20 # macro
PCI_BRIDGE_CTL_BUS_RESET = 0x40 # macro
PCI_BRIDGE_CTL_FAST_BACK = 0x80 # macro
PCI_CB_CAPABILITY_LIST = 0x14 # macro
PCI_CB_SEC_STATUS = 0x16 # macro
PCI_CB_PRIMARY_BUS = 0x18 # macro
PCI_CB_CARD_BUS = 0x19 # macro
PCI_CB_SUBORDINATE_BUS = 0x1a # macro
PCI_CB_LATENCY_TIMER = 0x1b # macro
PCI_CB_MEMORY_BASE_0 = 0x1c # macro
PCI_CB_MEMORY_LIMIT_0 = 0x20 # macro
PCI_CB_MEMORY_BASE_1 = 0x24 # macro
PCI_CB_MEMORY_LIMIT_1 = 0x28 # macro
PCI_CB_IO_BASE_0 = 0x2c # macro
PCI_CB_IO_BASE_0_HI = 0x2e # macro
PCI_CB_IO_LIMIT_0 = 0x30 # macro
PCI_CB_IO_LIMIT_0_HI = 0x32 # macro
PCI_CB_IO_BASE_1 = 0x34 # macro
PCI_CB_IO_BASE_1_HI = 0x36 # macro
PCI_CB_IO_LIMIT_1 = 0x38 # macro
PCI_CB_IO_LIMIT_1_HI = 0x3a # macro
PCI_CB_IO_RANGE_MASK = (~0x03) # macro
PCI_CB_BRIDGE_CONTROL = 0x3e # macro
PCI_CB_BRIDGE_CTL_PARITY = 0x01 # macro
PCI_CB_BRIDGE_CTL_SERR = 0x02 # macro
PCI_CB_BRIDGE_CTL_ISA = 0x04 # macro
PCI_CB_BRIDGE_CTL_VGA = 0x08 # macro
PCI_CB_BRIDGE_CTL_MASTER_ABORT = 0x20 # macro
PCI_CB_BRIDGE_CTL_CB_RESET = 0x40 # macro
PCI_CB_BRIDGE_CTL_16BIT_INT = 0x80 # macro
PCI_CB_BRIDGE_CTL_PREFETCH_MEM0 = 0x100 # macro
PCI_CB_BRIDGE_CTL_PREFETCH_MEM1 = 0x200 # macro
PCI_CB_BRIDGE_CTL_POST_WRITES = 0x400 # macro
PCI_CB_SUBSYSTEM_VENDOR_ID = 0x40 # macro
PCI_CB_SUBSYSTEM_ID = 0x42 # macro
PCI_CB_LEGACY_MODE_BASE = 0x44 # macro
PCI_CAP_LIST_ID = 0 # macro
PCI_CAP_ID_PM = 0x01 # macro
PCI_CAP_ID_AGP = 0x02 # macro
PCI_CAP_ID_VPD = 0x03 # macro
PCI_CAP_ID_SLOTID = 0x04 # macro
PCI_CAP_ID_MSI = 0x05 # macro
PCI_CAP_ID_CHSWP = 0x06 # macro
PCI_CAP_ID_PCIX = 0x07 # macro
PCI_CAP_ID_HT = 0x08 # macro
PCI_CAP_ID_VNDR = 0x09 # macro
PCI_CAP_ID_DBG = 0x0A # macro
PCI_CAP_ID_CCRC = 0x0B # macro
PCI_CAP_ID_SHPC = 0x0C # macro
PCI_CAP_ID_SSVID = 0x0D # macro
PCI_CAP_ID_AGP3 = 0x0E # macro
PCI_CAP_ID_SECDEV = 0x0F # macro
PCI_CAP_ID_EXP = 0x10 # macro
PCI_CAP_ID_MSIX = 0x11 # macro
PCI_CAP_ID_SATA = 0x12 # macro
PCI_CAP_ID_AF = 0x13 # macro
PCI_CAP_ID_EA = 0x14 # macro
PCI_CAP_ID_MAX = 0x14 # macro
PCI_CAP_LIST_NEXT = 1 # macro
PCI_CAP_FLAGS = 2 # macro
PCI_CAP_SIZEOF = 4 # macro
PCI_PM_PMC = 2 # macro
PCI_PM_CAP_VER_MASK = 0x0007 # macro
PCI_PM_CAP_PME_CLOCK = 0x0008 # macro
PCI_PM_CAP_RESERVED = 0x0010 # macro
PCI_PM_CAP_DSI = 0x0020 # macro
PCI_PM_CAP_AUX_POWER = 0x01C0 # macro
PCI_PM_CAP_D1 = 0x0200 # macro
PCI_PM_CAP_D2 = 0x0400 # macro
PCI_PM_CAP_PME = 0x0800 # macro
PCI_PM_CAP_PME_MASK = 0xF800 # macro
PCI_PM_CAP_PME_D0 = 0x0800 # macro
PCI_PM_CAP_PME_D1 = 0x1000 # macro
PCI_PM_CAP_PME_D2 = 0x2000 # macro
PCI_PM_CAP_PME_D3hot = 0x4000 # macro
PCI_PM_CAP_PME_D3cold = 0x8000 # macro
PCI_PM_CAP_PME_SHIFT = 11 # macro
PCI_PM_CTRL = 4 # macro
PCI_PM_CTRL_STATE_MASK = 0x0003 # macro
PCI_PM_CTRL_NO_SOFT_RESET = 0x0008 # macro
PCI_PM_CTRL_PME_ENABLE = 0x0100 # macro
PCI_PM_CTRL_DATA_SEL_MASK = 0x1e00 # macro
PCI_PM_CTRL_DATA_SCALE_MASK = 0x6000 # macro
PCI_PM_CTRL_PME_STATUS = 0x8000 # macro
PCI_PM_PPB_EXTENSIONS = 6 # macro
PCI_PM_PPB_B2_B3 = 0x40 # macro
PCI_PM_BPCC_ENABLE = 0x80 # macro
PCI_PM_DATA_REGISTER = 7 # macro
PCI_PM_SIZEOF = 8 # macro
PCI_AGP_VERSION = 2 # macro
PCI_AGP_RFU = 3 # macro
PCI_AGP_STATUS = 4 # macro
PCI_AGP_STATUS_RQ_MASK = 0xff000000 # macro
PCI_AGP_STATUS_SBA = 0x0200 # macro
PCI_AGP_STATUS_64BIT = 0x0020 # macro
PCI_AGP_STATUS_FW = 0x0010 # macro
PCI_AGP_STATUS_RATE4 = 0x0004 # macro
PCI_AGP_STATUS_RATE2 = 0x0002 # macro
PCI_AGP_STATUS_RATE1 = 0x0001 # macro
PCI_AGP_COMMAND = 8 # macro
PCI_AGP_COMMAND_RQ_MASK = 0xff000000 # macro
PCI_AGP_COMMAND_SBA = 0x0200 # macro
PCI_AGP_COMMAND_AGP = 0x0100 # macro
PCI_AGP_COMMAND_64BIT = 0x0020 # macro
PCI_AGP_COMMAND_FW = 0x0010 # macro
PCI_AGP_COMMAND_RATE4 = 0x0004 # macro
PCI_AGP_COMMAND_RATE2 = 0x0002 # macro
PCI_AGP_COMMAND_RATE1 = 0x0001 # macro
PCI_AGP_SIZEOF = 12 # macro
PCI_VPD_ADDR = 2 # macro
PCI_VPD_ADDR_MASK = 0x7fff # macro
PCI_VPD_ADDR_F = 0x8000 # macro
PCI_VPD_DATA = 4 # macro
PCI_CAP_VPD_SIZEOF = 8 # macro
PCI_SID_ESR = 2 # macro
PCI_SID_ESR_NSLOTS = 0x1f # macro
PCI_SID_ESR_FIC = 0x20 # macro
PCI_SID_CHASSIS_NR = 3 # macro
PCI_MSI_FLAGS = 2 # macro
PCI_MSI_FLAGS_ENABLE = 0x0001 # macro
PCI_MSI_FLAGS_QMASK = 0x000e # macro
PCI_MSI_FLAGS_QSIZE = 0x0070 # macro
PCI_MSI_FLAGS_64BIT = 0x0080 # macro
PCI_MSI_FLAGS_MASKBIT = 0x0100 # macro
PCI_MSI_RFU = 3 # macro
PCI_MSI_ADDRESS_LO = 4 # macro
PCI_MSI_ADDRESS_HI = 8 # macro
PCI_MSI_DATA_32 = 8 # macro
PCI_MSI_MASK_32 = 12 # macro
PCI_MSI_PENDING_32 = 16 # macro
PCI_MSI_DATA_64 = 12 # macro
PCI_MSI_MASK_64 = 16 # macro
PCI_MSI_PENDING_64 = 20 # macro
PCI_MSIX_FLAGS = 2 # macro
PCI_MSIX_FLAGS_QSIZE = 0x07FF # macro
PCI_MSIX_FLAGS_MASKALL = 0x4000 # macro
PCI_MSIX_FLAGS_ENABLE = 0x8000 # macro
PCI_MSIX_TABLE = 4 # macro
PCI_MSIX_TABLE_BIR = 0x00000007 # macro
PCI_MSIX_TABLE_OFFSET = 0xfffffff8 # macro
PCI_MSIX_PBA = 8 # macro
PCI_MSIX_PBA_BIR = 0x00000007 # macro
PCI_MSIX_PBA_OFFSET = 0xfffffff8 # macro
PCI_MSIX_FLAGS_BIRMASK = 0x00000007 # macro
PCI_CAP_MSIX_SIZEOF = 12 # macro
PCI_MSIX_ENTRY_SIZE = 16 # macro
PCI_MSIX_ENTRY_LOWER_ADDR = 0 # macro
PCI_MSIX_ENTRY_UPPER_ADDR = 4 # macro
PCI_MSIX_ENTRY_DATA = 8 # macro
PCI_MSIX_ENTRY_VECTOR_CTRL = 12 # macro
PCI_MSIX_ENTRY_CTRL_MASKBIT = 0x00000001 # macro
PCI_CHSWP_CSR = 2 # macro
PCI_CHSWP_DHA = 0x01 # macro
PCI_CHSWP_EIM = 0x02 # macro
PCI_CHSWP_PIE = 0x04 # macro
PCI_CHSWP_LOO = 0x08 # macro
PCI_CHSWP_PI = 0x30 # macro
PCI_CHSWP_EXT = 0x40 # macro
PCI_CHSWP_INS = 0x80 # macro
PCI_AF_LENGTH = 2 # macro
PCI_AF_CAP = 3 # macro
PCI_AF_CAP_TP = 0x01 # macro
PCI_AF_CAP_FLR = 0x02 # macro
PCI_AF_CTRL = 4 # macro
PCI_AF_CTRL_FLR = 0x01 # macro
PCI_AF_STATUS = 5 # macro
PCI_AF_STATUS_TP = 0x01 # macro
PCI_CAP_AF_SIZEOF = 6 # macro
PCI_EA_NUM_ENT = 2 # macro
PCI_EA_NUM_ENT_MASK = 0x3f # macro
PCI_EA_FIRST_ENT = 4 # macro
PCI_EA_FIRST_ENT_BRIDGE = 8 # macro
PCI_EA_ES = 0x00000007 # macro
PCI_EA_BEI = 0x000000f0 # macro
PCI_EA_SEC_BUS_MASK = 0xff # macro
PCI_EA_SUB_BUS_MASK = 0xff00 # macro
PCI_EA_SUB_BUS_SHIFT = 8 # macro
PCI_EA_BEI_BAR0 = 0 # macro
PCI_EA_BEI_BAR5 = 5 # macro
PCI_EA_BEI_BRIDGE = 6 # macro
PCI_EA_BEI_ENI = 7 # macro
PCI_EA_BEI_ROM = 8 # macro
PCI_EA_BEI_VF_BAR0 = 9 # macro
PCI_EA_BEI_VF_BAR5 = 14 # macro
PCI_EA_BEI_RESERVED = 15 # macro
PCI_EA_PP = 0x0000ff00 # macro
PCI_EA_SP = 0x00ff0000 # macro
PCI_EA_P_MEM = 0x00 # macro
PCI_EA_P_MEM_PREFETCH = 0x01 # macro
PCI_EA_P_IO = 0x02 # macro
PCI_EA_P_VF_MEM_PREFETCH = 0x03 # macro
PCI_EA_P_VF_MEM = 0x04 # macro
PCI_EA_P_BRIDGE_MEM = 0x05 # macro
PCI_EA_P_BRIDGE_MEM_PREFETCH = 0x06 # macro
PCI_EA_P_BRIDGE_IO = 0x07 # macro
PCI_EA_P_MEM_RESERVED = 0xfd # macro
PCI_EA_P_IO_RESERVED = 0xfe # macro
PCI_EA_P_UNAVAILABLE = 0xff # macro
PCI_EA_WRITABLE = 0x40000000 # macro
PCI_EA_ENABLE = 0x80000000 # macro
PCI_EA_BASE = 4 # macro
PCI_EA_MAX_OFFSET = 8 # macro
PCI_EA_IS_64 = 0x00000002 # macro
PCI_EA_FIELD_MASK = 0xfffffffc # macro
PCI_X_CMD = 2 # macro
PCI_X_CMD_DPERR_E = 0x0001 # macro
PCI_X_CMD_ERO = 0x0002 # macro
PCI_X_CMD_READ_512 = 0x0000 # macro
PCI_X_CMD_READ_1K = 0x0004 # macro
PCI_X_CMD_READ_2K = 0x0008 # macro
PCI_X_CMD_READ_4K = 0x000c # macro
PCI_X_CMD_MAX_READ = 0x000c # macro
PCI_X_CMD_SPLIT_1 = 0x0000 # macro
PCI_X_CMD_SPLIT_2 = 0x0010 # macro
PCI_X_CMD_SPLIT_3 = 0x0020 # macro
PCI_X_CMD_SPLIT_4 = 0x0030 # macro
PCI_X_CMD_SPLIT_8 = 0x0040 # macro
PCI_X_CMD_SPLIT_12 = 0x0050 # macro
PCI_X_CMD_SPLIT_16 = 0x0060 # macro
PCI_X_CMD_SPLIT_32 = 0x0070 # macro
PCI_X_CMD_MAX_SPLIT = 0x0070 # macro
def PCI_X_CMD_VERSION(x):  # macro
   return (((x)>>12)&3)
PCI_X_STATUS = 4 # macro
PCI_X_STATUS_DEVFN = 0x000000ff # macro
PCI_X_STATUS_BUS = 0x0000ff00 # macro
PCI_X_STATUS_64BIT = 0x00010000 # macro
PCI_X_STATUS_133MHZ = 0x00020000 # macro
PCI_X_STATUS_SPL_DISC = 0x00040000 # macro
PCI_X_STATUS_UNX_SPL = 0x00080000 # macro
PCI_X_STATUS_COMPLEX = 0x00100000 # macro
PCI_X_STATUS_MAX_READ = 0x00600000 # macro
PCI_X_STATUS_MAX_SPLIT = 0x03800000 # macro
PCI_X_STATUS_MAX_CUM = 0x1c000000 # macro
PCI_X_STATUS_SPL_ERR = 0x20000000 # macro
PCI_X_STATUS_266MHZ = 0x40000000 # macro
PCI_X_STATUS_533MHZ = 0x80000000 # macro
PCI_X_ECC_CSR = 8 # macro
PCI_CAP_PCIX_SIZEOF_V0 = 8 # macro
PCI_CAP_PCIX_SIZEOF_V1 = 24 # macro
PCI_CAP_PCIX_SIZEOF_V2 = 24 # macro
PCI_X_BRIDGE_SSTATUS = 2 # macro
PCI_X_SSTATUS_64BIT = 0x0001 # macro
PCI_X_SSTATUS_133MHZ = 0x0002 # macro
PCI_X_SSTATUS_FREQ = 0x03c0 # macro
PCI_X_SSTATUS_VERS = 0x3000 # macro
PCI_X_SSTATUS_V1 = 0x1000 # macro
PCI_X_SSTATUS_V2 = 0x2000 # macro
PCI_X_SSTATUS_266MHZ = 0x4000 # macro
PCI_X_SSTATUS_533MHZ = 0x8000 # macro
PCI_X_BRIDGE_STATUS = 4 # macro
PCI_SSVID_VENDOR_ID = 4 # macro
PCI_SSVID_DEVICE_ID = 6 # macro
PCI_EXP_FLAGS = 2 # macro
PCI_EXP_FLAGS_VERS = 0x000f # macro
PCI_EXP_FLAGS_TYPE = 0x00f0 # macro
PCI_EXP_TYPE_ENDPOINT = 0x0 # macro
PCI_EXP_TYPE_LEG_END = 0x1 # macro
PCI_EXP_TYPE_ROOT_PORT = 0x4 # macro
PCI_EXP_TYPE_UPSTREAM = 0x5 # macro
PCI_EXP_TYPE_DOWNSTREAM = 0x6 # macro
PCI_EXP_TYPE_PCI_BRIDGE = 0x7 # macro
PCI_EXP_TYPE_PCIE_BRIDGE = 0x8 # macro
PCI_EXP_TYPE_RC_END = 0x9 # macro
PCI_EXP_TYPE_RC_EC = 0xa # macro
PCI_EXP_FLAGS_SLOT = 0x0100 # macro
PCI_EXP_FLAGS_IRQ = 0x3e00 # macro
PCI_EXP_DEVCAP = 4 # macro
PCI_EXP_DEVCAP_PAYLOAD = 0x00000007 # macro
PCI_EXP_DEVCAP_PHANTOM = 0x00000018 # macro
PCI_EXP_DEVCAP_EXT_TAG = 0x00000020 # macro
PCI_EXP_DEVCAP_L0S = 0x000001c0 # macro
PCI_EXP_DEVCAP_L1 = 0x00000e00 # macro
PCI_EXP_DEVCAP_ATN_BUT = 0x00001000 # macro
PCI_EXP_DEVCAP_ATN_IND = 0x00002000 # macro
PCI_EXP_DEVCAP_PWR_IND = 0x00004000 # macro
PCI_EXP_DEVCAP_RBER = 0x00008000 # macro
PCI_EXP_DEVCAP_PWR_VAL = 0x03fc0000 # macro
PCI_EXP_DEVCAP_PWR_SCL = 0x0c000000 # macro
PCI_EXP_DEVCAP_FLR = 0x10000000 # macro
PCI_EXP_DEVCTL = 8 # macro
PCI_EXP_DEVCTL_CERE = 0x0001 # macro
PCI_EXP_DEVCTL_NFERE = 0x0002 # macro
PCI_EXP_DEVCTL_FERE = 0x0004 # macro
PCI_EXP_DEVCTL_URRE = 0x0008 # macro
PCI_EXP_DEVCTL_RELAX_EN = 0x0010 # macro
PCI_EXP_DEVCTL_PAYLOAD = 0x00e0 # macro
PCI_EXP_DEVCTL_PAYLOAD_128B = 0x0000 # macro
PCI_EXP_DEVCTL_PAYLOAD_256B = 0x0020 # macro
PCI_EXP_DEVCTL_PAYLOAD_512B = 0x0040 # macro
PCI_EXP_DEVCTL_PAYLOAD_1024B = 0x0060 # macro
PCI_EXP_DEVCTL_PAYLOAD_2048B = 0x0080 # macro
PCI_EXP_DEVCTL_PAYLOAD_4096B = 0x00a0 # macro
PCI_EXP_DEVCTL_EXT_TAG = 0x0100 # macro
PCI_EXP_DEVCTL_PHANTOM = 0x0200 # macro
PCI_EXP_DEVCTL_AUX_PME = 0x0400 # macro
PCI_EXP_DEVCTL_NOSNOOP_EN = 0x0800 # macro
PCI_EXP_DEVCTL_READRQ = 0x7000 # macro
PCI_EXP_DEVCTL_READRQ_128B = 0x0000 # macro
PCI_EXP_DEVCTL_READRQ_256B = 0x1000 # macro
PCI_EXP_DEVCTL_READRQ_512B = 0x2000 # macro
PCI_EXP_DEVCTL_READRQ_1024B = 0x3000 # macro
PCI_EXP_DEVCTL_READRQ_2048B = 0x4000 # macro
PCI_EXP_DEVCTL_READRQ_4096B = 0x5000 # macro
PCI_EXP_DEVCTL_BCR_FLR = 0x8000 # macro
PCI_EXP_DEVSTA = 10 # macro
PCI_EXP_DEVSTA_CED = 0x0001 # macro
PCI_EXP_DEVSTA_NFED = 0x0002 # macro
PCI_EXP_DEVSTA_FED = 0x0004 # macro
PCI_EXP_DEVSTA_URD = 0x0008 # macro
PCI_EXP_DEVSTA_AUXPD = 0x0010 # macro
PCI_EXP_DEVSTA_TRPND = 0x0020 # macro
PCI_CAP_EXP_RC_ENDPOINT_SIZEOF_V1 = 12 # macro
PCI_EXP_LNKCAP = 12 # macro
PCI_EXP_LNKCAP_SLS = 0x0000000f # macro
PCI_EXP_LNKCAP_SLS_2_5GB = 0x00000001 # macro
PCI_EXP_LNKCAP_SLS_5_0GB = 0x00000002 # macro
PCI_EXP_LNKCAP_SLS_8_0GB = 0x00000003 # macro
PCI_EXP_LNKCAP_SLS_16_0GB = 0x00000004 # macro
PCI_EXP_LNKCAP_SLS_32_0GB = 0x00000005 # macro
PCI_EXP_LNKCAP_SLS_64_0GB = 0x00000006 # macro
PCI_EXP_LNKCAP_MLW = 0x000003f0 # macro
PCI_EXP_LNKCAP_ASPMS = 0x00000c00 # macro
PCI_EXP_LNKCAP_ASPM_L0S = 0x00000400 # macro
PCI_EXP_LNKCAP_ASPM_L1 = 0x00000800 # macro
PCI_EXP_LNKCAP_L0SEL = 0x00007000 # macro
PCI_EXP_LNKCAP_L1EL = 0x00038000 # macro
PCI_EXP_LNKCAP_CLKPM = 0x00040000 # macro
PCI_EXP_LNKCAP_SDERC = 0x00080000 # macro
PCI_EXP_LNKCAP_DLLLARC = 0x00100000 # macro
PCI_EXP_LNKCAP_LBNC = 0x00200000 # macro
PCI_EXP_LNKCAP_PN = 0xff000000 # macro
PCI_EXP_LNKCTL = 16 # macro
PCI_EXP_LNKCTL_ASPMC = 0x0003 # macro
PCI_EXP_LNKCTL_ASPM_L0S = 0x0001 # macro
PCI_EXP_LNKCTL_ASPM_L1 = 0x0002 # macro
PCI_EXP_LNKCTL_RCB = 0x0008 # macro
PCI_EXP_LNKCTL_LD = 0x0010 # macro
PCI_EXP_LNKCTL_RL = 0x0020 # macro
PCI_EXP_LNKCTL_CCC = 0x0040 # macro
PCI_EXP_LNKCTL_ES = 0x0080 # macro
PCI_EXP_LNKCTL_CLKREQ_EN = 0x0100 # macro
PCI_EXP_LNKCTL_HAWD = 0x0200 # macro
PCI_EXP_LNKCTL_LBMIE = 0x0400 # macro
PCI_EXP_LNKCTL_LABIE = 0x0800 # macro
PCI_EXP_LNKSTA = 18 # macro
PCI_EXP_LNKSTA_CLS = 0x000f # macro
PCI_EXP_LNKSTA_CLS_2_5GB = 0x0001 # macro
PCI_EXP_LNKSTA_CLS_5_0GB = 0x0002 # macro
PCI_EXP_LNKSTA_CLS_8_0GB = 0x0003 # macro
PCI_EXP_LNKSTA_CLS_16_0GB = 0x0004 # macro
PCI_EXP_LNKSTA_CLS_32_0GB = 0x0005 # macro
PCI_EXP_LNKSTA_CLS_64_0GB = 0x0006 # macro
PCI_EXP_LNKSTA_NLW = 0x03f0 # macro
PCI_EXP_LNKSTA_NLW_X1 = 0x0010 # macro
PCI_EXP_LNKSTA_NLW_X2 = 0x0020 # macro
PCI_EXP_LNKSTA_NLW_X4 = 0x0040 # macro
PCI_EXP_LNKSTA_NLW_X8 = 0x0080 # macro
PCI_EXP_LNKSTA_NLW_SHIFT = 4 # macro
PCI_EXP_LNKSTA_LT = 0x0800 # macro
PCI_EXP_LNKSTA_SLC = 0x1000 # macro
PCI_EXP_LNKSTA_DLLLA = 0x2000 # macro
PCI_EXP_LNKSTA_LBMS = 0x4000 # macro
PCI_EXP_LNKSTA_LABS = 0x8000 # macro
PCI_CAP_EXP_ENDPOINT_SIZEOF_V1 = 20 # macro
PCI_EXP_SLTCAP = 20 # macro
PCI_EXP_SLTCAP_ABP = 0x00000001 # macro
PCI_EXP_SLTCAP_PCP = 0x00000002 # macro
PCI_EXP_SLTCAP_MRLSP = 0x00000004 # macro
PCI_EXP_SLTCAP_AIP = 0x00000008 # macro
PCI_EXP_SLTCAP_PIP = 0x00000010 # macro
PCI_EXP_SLTCAP_HPS = 0x00000020 # macro
PCI_EXP_SLTCAP_HPC = 0x00000040 # macro
PCI_EXP_SLTCAP_SPLV = 0x00007f80 # macro
PCI_EXP_SLTCAP_SPLS = 0x00018000 # macro
PCI_EXP_SLTCAP_EIP = 0x00020000 # macro
PCI_EXP_SLTCAP_NCCS = 0x00040000 # macro
PCI_EXP_SLTCAP_PSN = 0xfff80000 # macro
PCI_EXP_SLTCTL = 24 # macro
PCI_EXP_SLTCTL_ABPE = 0x0001 # macro
PCI_EXP_SLTCTL_PFDE = 0x0002 # macro
PCI_EXP_SLTCTL_MRLSCE = 0x0004 # macro
PCI_EXP_SLTCTL_PDCE = 0x0008 # macro
PCI_EXP_SLTCTL_CCIE = 0x0010 # macro
PCI_EXP_SLTCTL_HPIE = 0x0020 # macro
PCI_EXP_SLTCTL_AIC = 0x00c0 # macro
PCI_EXP_SLTCTL_ATTN_IND_SHIFT = 6 # macro
PCI_EXP_SLTCTL_ATTN_IND_ON = 0x0040 # macro
PCI_EXP_SLTCTL_ATTN_IND_BLINK = 0x0080 # macro
PCI_EXP_SLTCTL_ATTN_IND_OFF = 0x00c0 # macro
PCI_EXP_SLTCTL_PIC = 0x0300 # macro
PCI_EXP_SLTCTL_PWR_IND_ON = 0x0100 # macro
PCI_EXP_SLTCTL_PWR_IND_BLINK = 0x0200 # macro
PCI_EXP_SLTCTL_PWR_IND_OFF = 0x0300 # macro
PCI_EXP_SLTCTL_PCC = 0x0400 # macro
PCI_EXP_SLTCTL_PWR_ON = 0x0000 # macro
PCI_EXP_SLTCTL_PWR_OFF = 0x0400 # macro
PCI_EXP_SLTCTL_EIC = 0x0800 # macro
PCI_EXP_SLTCTL_DLLSCE = 0x1000 # macro
PCI_EXP_SLTCTL_IBPD_DISABLE = 0x4000 # macro
PCI_EXP_SLTSTA = 26 # macro
PCI_EXP_SLTSTA_ABP = 0x0001 # macro
PCI_EXP_SLTSTA_PFD = 0x0002 # macro
PCI_EXP_SLTSTA_MRLSC = 0x0004 # macro
PCI_EXP_SLTSTA_PDC = 0x0008 # macro
PCI_EXP_SLTSTA_CC = 0x0010 # macro
PCI_EXP_SLTSTA_MRLSS = 0x0020 # macro
PCI_EXP_SLTSTA_PDS = 0x0040 # macro
PCI_EXP_SLTSTA_EIS = 0x0080 # macro
PCI_EXP_SLTSTA_DLLSC = 0x0100 # macro
PCI_EXP_RTCTL = 28 # macro
PCI_EXP_RTCTL_SECEE = 0x0001 # macro
PCI_EXP_RTCTL_SENFEE = 0x0002 # macro
PCI_EXP_RTCTL_SEFEE = 0x0004 # macro
PCI_EXP_RTCTL_PMEIE = 0x0008 # macro
PCI_EXP_RTCTL_CRSSVE = 0x0010 # macro
PCI_EXP_RTCAP = 30 # macro
PCI_EXP_RTCAP_CRSVIS = 0x0001 # macro
PCI_EXP_RTSTA = 32 # macro
PCI_EXP_RTSTA_PME = 0x00010000 # macro
PCI_EXP_RTSTA_PENDING = 0x00020000 # macro
PCI_EXP_DEVCAP2 = 36 # macro
PCI_EXP_DEVCAP2_COMP_TMOUT_DIS = 0x00000010 # macro
PCI_EXP_DEVCAP2_ARI = 0x00000020 # macro
PCI_EXP_DEVCAP2_ATOMIC_ROUTE = 0x00000040 # macro
PCI_EXP_DEVCAP2_ATOMIC_COMP32 = 0x00000080 # macro
PCI_EXP_DEVCAP2_ATOMIC_COMP64 = 0x00000100 # macro
PCI_EXP_DEVCAP2_ATOMIC_COMP128 = 0x00000200 # macro
PCI_EXP_DEVCAP2_LTR = 0x00000800 # macro
PCI_EXP_DEVCAP2_OBFF_MASK = 0x000c0000 # macro
PCI_EXP_DEVCAP2_OBFF_MSG = 0x00040000 # macro
PCI_EXP_DEVCAP2_OBFF_WAKE = 0x00080000 # macro
PCI_EXP_DEVCAP2_EE_PREFIX = 0x00200000 # macro
PCI_EXP_DEVCTL2 = 40 # macro
PCI_EXP_DEVCTL2_COMP_TIMEOUT = 0x000f # macro
PCI_EXP_DEVCTL2_COMP_TMOUT_DIS = 0x0010 # macro
PCI_EXP_DEVCTL2_ARI = 0x0020 # macro
PCI_EXP_DEVCTL2_ATOMIC_REQ = 0x0040 # macro
PCI_EXP_DEVCTL2_ATOMIC_EGRESS_BLOCK = 0x0080 # macro
PCI_EXP_DEVCTL2_IDO_REQ_EN = 0x0100 # macro
PCI_EXP_DEVCTL2_IDO_CMP_EN = 0x0200 # macro
PCI_EXP_DEVCTL2_LTR_EN = 0x0400 # macro
PCI_EXP_DEVCTL2_OBFF_MSGA_EN = 0x2000 # macro
PCI_EXP_DEVCTL2_OBFF_MSGB_EN = 0x4000 # macro
PCI_EXP_DEVCTL2_OBFF_WAKE_EN = 0x6000 # macro
PCI_EXP_DEVSTA2 = 42 # macro
PCI_CAP_EXP_RC_ENDPOINT_SIZEOF_V2 = 44 # macro
PCI_EXP_LNKCAP2 = 44 # macro
PCI_EXP_LNKCAP2_SLS_2_5GB = 0x00000002 # macro
PCI_EXP_LNKCAP2_SLS_5_0GB = 0x00000004 # macro
PCI_EXP_LNKCAP2_SLS_8_0GB = 0x00000008 # macro
PCI_EXP_LNKCAP2_SLS_16_0GB = 0x00000010 # macro
PCI_EXP_LNKCAP2_SLS_32_0GB = 0x00000020 # macro
PCI_EXP_LNKCAP2_SLS_64_0GB = 0x00000040 # macro
PCI_EXP_LNKCAP2_CROSSLINK = 0x00000100 # macro
PCI_EXP_LNKCTL2 = 48 # macro
PCI_EXP_LNKCTL2_TLS = 0x000f # macro
PCI_EXP_LNKCTL2_TLS_2_5GT = 0x0001 # macro
PCI_EXP_LNKCTL2_TLS_5_0GT = 0x0002 # macro
PCI_EXP_LNKCTL2_TLS_8_0GT = 0x0003 # macro
PCI_EXP_LNKCTL2_TLS_16_0GT = 0x0004 # macro
PCI_EXP_LNKCTL2_TLS_32_0GT = 0x0005 # macro
PCI_EXP_LNKCTL2_TLS_64_0GT = 0x0006 # macro
PCI_EXP_LNKCTL2_ENTER_COMP = 0x0010 # macro
PCI_EXP_LNKCTL2_TX_MARGIN = 0x0380 # macro
PCI_EXP_LNKCTL2_HASD = 0x0020 # macro
PCI_EXP_LNKSTA2 = 50 # macro
PCI_CAP_EXP_ENDPOINT_SIZEOF_V2 = 52 # macro
PCI_EXP_SLTCAP2 = 52 # macro
PCI_EXP_SLTCAP2_IBPD = 0x00000001 # macro
PCI_EXP_SLTCTL2 = 56 # macro
PCI_EXP_SLTSTA2 = 58 # macro
def PCI_EXT_CAP_ID(header):  # macro
   return (header&0x0000ffff)
def PCI_EXT_CAP_VER(header):  # macro
   return ((header>>16)&0xf)
def PCI_EXT_CAP_NEXT(header):  # macro
   return ((header>>20)&0xffc)
PCI_EXT_CAP_ID_ERR = 0x01 # macro
PCI_EXT_CAP_ID_VC = 0x02 # macro
PCI_EXT_CAP_ID_DSN = 0x03 # macro
PCI_EXT_CAP_ID_PWR = 0x04 # macro
PCI_EXT_CAP_ID_RCLD = 0x05 # macro
PCI_EXT_CAP_ID_RCILC = 0x06 # macro
PCI_EXT_CAP_ID_RCEC = 0x07 # macro
PCI_EXT_CAP_ID_MFVC = 0x08 # macro
PCI_EXT_CAP_ID_VC9 = 0x09 # macro
PCI_EXT_CAP_ID_RCRB = 0x0A # macro
PCI_EXT_CAP_ID_VNDR = 0x0B # macro
PCI_EXT_CAP_ID_CAC = 0x0C # macro
PCI_EXT_CAP_ID_ACS = 0x0D # macro
PCI_EXT_CAP_ID_ARI = 0x0E # macro
PCI_EXT_CAP_ID_ATS = 0x0F # macro
PCI_EXT_CAP_ID_SRIOV = 0x10 # macro
PCI_EXT_CAP_ID_MRIOV = 0x11 # macro
PCI_EXT_CAP_ID_MCAST = 0x12 # macro
PCI_EXT_CAP_ID_PRI = 0x13 # macro
PCI_EXT_CAP_ID_AMD_XXX = 0x14 # macro
PCI_EXT_CAP_ID_REBAR = 0x15 # macro
PCI_EXT_CAP_ID_DPA = 0x16 # macro
PCI_EXT_CAP_ID_TPH = 0x17 # macro
PCI_EXT_CAP_ID_LTR = 0x18 # macro
PCI_EXT_CAP_ID_SECPCI = 0x19 # macro
PCI_EXT_CAP_ID_PMUX = 0x1A # macro
PCI_EXT_CAP_ID_PASID = 0x1B # macro
PCI_EXT_CAP_ID_DPC = 0x1D # macro
PCI_EXT_CAP_ID_L1SS = 0x1E # macro
PCI_EXT_CAP_ID_PTM = 0x1F # macro
PCI_EXT_CAP_ID_DVSEC = 0x23 # macro
PCI_EXT_CAP_ID_DLF = 0x25 # macro
PCI_EXT_CAP_ID_PL_16GT = 0x26 # macro
PCI_EXT_CAP_ID_MAX = 0x26 # macro
PCI_EXT_CAP_DSN_SIZEOF = 12 # macro
PCI_EXT_CAP_MCAST_ENDPOINT_SIZEOF = 40 # macro
PCI_ERR_UNCOR_STATUS = 4 # macro
PCI_ERR_UNC_UND = 0x00000001 # macro
PCI_ERR_UNC_DLP = 0x00000010 # macro
PCI_ERR_UNC_SURPDN = 0x00000020 # macro
PCI_ERR_UNC_POISON_TLP = 0x00001000 # macro
PCI_ERR_UNC_FCP = 0x00002000 # macro
PCI_ERR_UNC_COMP_TIME = 0x00004000 # macro
PCI_ERR_UNC_COMP_ABORT = 0x00008000 # macro
PCI_ERR_UNC_UNX_COMP = 0x00010000 # macro
PCI_ERR_UNC_RX_OVER = 0x00020000 # macro
PCI_ERR_UNC_MALF_TLP = 0x00040000 # macro
PCI_ERR_UNC_ECRC = 0x00080000 # macro
PCI_ERR_UNC_UNSUP = 0x00100000 # macro
PCI_ERR_UNC_ACSV = 0x00200000 # macro
PCI_ERR_UNC_INTN = 0x00400000 # macro
PCI_ERR_UNC_MCBTLP = 0x00800000 # macro
PCI_ERR_UNC_ATOMEG = 0x01000000 # macro
PCI_ERR_UNC_TLPPRE = 0x02000000 # macro
PCI_ERR_UNCOR_MASK = 8 # macro
PCI_ERR_UNCOR_SEVER = 12 # macro
PCI_ERR_COR_STATUS = 16 # macro
PCI_ERR_COR_RCVR = 0x00000001 # macro
PCI_ERR_COR_BAD_TLP = 0x00000040 # macro
PCI_ERR_COR_BAD_DLLP = 0x00000080 # macro
PCI_ERR_COR_REP_ROLL = 0x00000100 # macro
PCI_ERR_COR_REP_TIMER = 0x00001000 # macro
PCI_ERR_COR_ADV_NFAT = 0x00002000 # macro
PCI_ERR_COR_INTERNAL = 0x00004000 # macro
PCI_ERR_COR_LOG_OVER = 0x00008000 # macro
PCI_ERR_COR_MASK = 20 # macro
PCI_ERR_CAP = 24 # macro
def PCI_ERR_CAP_FEP(x):  # macro
   return ((x)&31)
PCI_ERR_CAP_ECRC_GENC = 0x00000020 # macro
PCI_ERR_CAP_ECRC_GENE = 0x00000040 # macro
PCI_ERR_CAP_ECRC_CHKC = 0x00000080 # macro
PCI_ERR_CAP_ECRC_CHKE = 0x00000100 # macro
PCI_ERR_HEADER_LOG = 28 # macro
PCI_ERR_ROOT_COMMAND = 44 # macro
PCI_ERR_ROOT_CMD_COR_EN = 0x00000001 # macro
PCI_ERR_ROOT_CMD_NONFATAL_EN = 0x00000002 # macro
PCI_ERR_ROOT_CMD_FATAL_EN = 0x00000004 # macro
PCI_ERR_ROOT_STATUS = 48 # macro
PCI_ERR_ROOT_COR_RCV = 0x00000001 # macro
PCI_ERR_ROOT_MULTI_COR_RCV = 0x00000002 # macro
PCI_ERR_ROOT_UNCOR_RCV = 0x00000004 # macro
PCI_ERR_ROOT_MULTI_UNCOR_RCV = 0x00000008 # macro
PCI_ERR_ROOT_FIRST_FATAL = 0x00000010 # macro
PCI_ERR_ROOT_NONFATAL_RCV = 0x00000020 # macro
PCI_ERR_ROOT_FATAL_RCV = 0x00000040 # macro
PCI_ERR_ROOT_AER_IRQ = 0xf8000000 # macro
PCI_ERR_ROOT_ERR_SRC = 52 # macro
PCI_VC_PORT_CAP1 = 4 # macro
PCI_VC_CAP1_EVCC = 0x00000007 # macro
PCI_VC_CAP1_LPEVCC = 0x00000070 # macro
PCI_VC_CAP1_ARB_SIZE = 0x00000c00 # macro
PCI_VC_PORT_CAP2 = 8 # macro
PCI_VC_CAP2_32_PHASE = 0x00000002 # macro
PCI_VC_CAP2_64_PHASE = 0x00000004 # macro
PCI_VC_CAP2_128_PHASE = 0x00000008 # macro
PCI_VC_CAP2_ARB_OFF = 0xff000000 # macro
PCI_VC_PORT_CTRL = 12 # macro
PCI_VC_PORT_CTRL_LOAD_TABLE = 0x00000001 # macro
PCI_VC_PORT_STATUS = 14 # macro
PCI_VC_PORT_STATUS_TABLE = 0x00000001 # macro
PCI_VC_RES_CAP = 16 # macro
PCI_VC_RES_CAP_32_PHASE = 0x00000002 # macro
PCI_VC_RES_CAP_64_PHASE = 0x00000004 # macro
PCI_VC_RES_CAP_128_PHASE = 0x00000008 # macro
PCI_VC_RES_CAP_128_PHASE_TB = 0x00000010 # macro
PCI_VC_RES_CAP_256_PHASE = 0x00000020 # macro
PCI_VC_RES_CAP_ARB_OFF = 0xff000000 # macro
PCI_VC_RES_CTRL = 20 # macro
PCI_VC_RES_CTRL_LOAD_TABLE = 0x00010000 # macro
PCI_VC_RES_CTRL_ARB_SELECT = 0x000e0000 # macro
PCI_VC_RES_CTRL_ID = 0x07000000 # macro
PCI_VC_RES_CTRL_ENABLE = 0x80000000 # macro
PCI_VC_RES_STATUS = 26 # macro
PCI_VC_RES_STATUS_TABLE = 0x00000001 # macro
PCI_VC_RES_STATUS_NEGO = 0x00000002 # macro
PCI_CAP_VC_BASE_SIZEOF = 0x10 # macro
PCI_CAP_VC_PER_VC_SIZEOF = 0x0C # macro
PCI_PWR_DSR = 4 # macro
PCI_PWR_DATA = 8 # macro
def PCI_PWR_DATA_BASE(x):  # macro
   return ((x)&0xff)
def PCI_PWR_DATA_SCALE(x):  # macro
   return (((x)>>8)&3)
def PCI_PWR_DATA_PM_SUB(x):  # macro
   return (((x)>>10)&7)
def PCI_PWR_DATA_PM_STATE(x):  # macro
   return (((x)>>13)&3)
def PCI_PWR_DATA_TYPE(x):  # macro
   return (((x)>>15)&7)
def PCI_PWR_DATA_RAIL(x):  # macro
   return (((x)>>18)&7)
PCI_PWR_CAP = 12 # macro
def PCI_PWR_CAP_BUDGET(x):  # macro
   return ((x)&1)
PCI_EXT_CAP_PWR_SIZEOF = 16 # macro
PCI_RCEC_RCIEP_BITMAP = 4 # macro
PCI_RCEC_BUSN = 8 # macro
PCI_RCEC_BUSN_REG_VER = 0x02 # macro
def PCI_RCEC_BUSN_NEXT(x):  # macro
   return (((x)>>8)&0xff)
def PCI_RCEC_BUSN_LAST(x):  # macro
   return (((x)>>16)&0xff)
PCI_VNDR_HEADER = 4 # macro
def PCI_VNDR_HEADER_ID(x):  # macro
   return ((x)&0xffff)
def PCI_VNDR_HEADER_REV(x):  # macro
   return (((x)>>16)&0xf)
def PCI_VNDR_HEADER_LEN(x):  # macro
   return (((x)>>20)&0xfff)
HT_3BIT_CAP_MASK = 0xE0 # macro
HT_CAPTYPE_SLAVE = 0x00 # macro
HT_CAPTYPE_HOST = 0x20 # macro
HT_5BIT_CAP_MASK = 0xF8 # macro
HT_CAPTYPE_IRQ = 0x80 # macro
HT_CAPTYPE_REMAPPING_40 = 0xA0 # macro
HT_CAPTYPE_REMAPPING_64 = 0xA2 # macro
HT_CAPTYPE_UNITID_CLUMP = 0x90 # macro
HT_CAPTYPE_EXTCONF = 0x98 # macro
HT_CAPTYPE_MSI_MAPPING = 0xA8 # macro
HT_MSI_FLAGS = 0x02 # macro
HT_MSI_FLAGS_ENABLE = 0x1 # macro
HT_MSI_FLAGS_FIXED = 0x2 # macro
HT_MSI_FIXED_ADDR = 0x00000000FEE00000 # macro
HT_MSI_ADDR_LO = 0x04 # macro
HT_MSI_ADDR_LO_MASK = 0xFFF00000 # macro
HT_MSI_ADDR_HI = 0x08 # macro
HT_CAPTYPE_DIRECT_ROUTE = 0xB0 # macro
HT_CAPTYPE_VCSET = 0xB8 # macro
HT_CAPTYPE_ERROR_RETRY = 0xC0 # macro
HT_CAPTYPE_GEN3 = 0xD0 # macro
HT_CAPTYPE_PM = 0xE0 # macro
HT_CAP_SIZEOF_LONG = 28 # macro
HT_CAP_SIZEOF_SHORT = 24 # macro
PCI_ARI_CAP = 0x04 # macro
PCI_ARI_CAP_MFVC = 0x0001 # macro
PCI_ARI_CAP_ACS = 0x0002 # macro
def PCI_ARI_CAP_NFN(x):  # macro
   return (((x)>>8)&0xff)
PCI_ARI_CTRL = 0x06 # macro
PCI_ARI_CTRL_MFVC = 0x0001 # macro
PCI_ARI_CTRL_ACS = 0x0002 # macro
def PCI_ARI_CTRL_FG(x):  # macro
   return (((x)>>4)&7)
PCI_EXT_CAP_ARI_SIZEOF = 8 # macro
PCI_ATS_CAP = 0x04 # macro
def PCI_ATS_CAP_QDEP(x):  # macro
   return ((x)&0x1f)
PCI_ATS_MAX_QDEP = 32 # macro
PCI_ATS_CAP_PAGE_ALIGNED = 0x0020 # macro
PCI_ATS_CTRL = 0x06 # macro
PCI_ATS_CTRL_ENABLE = 0x8000 # macro
def PCI_ATS_CTRL_STU(x):  # macro
   return ((x)&0x1f)
PCI_ATS_MIN_STU = 12 # macro
PCI_EXT_CAP_ATS_SIZEOF = 8 # macro
PCI_PRI_CTRL = 0x04 # macro
PCI_PRI_CTRL_ENABLE = 0x0001 # macro
PCI_PRI_CTRL_RESET = 0x0002 # macro
PCI_PRI_STATUS = 0x06 # macro
PCI_PRI_STATUS_RF = 0x0001 # macro
PCI_PRI_STATUS_UPRGI = 0x0002 # macro
PCI_PRI_STATUS_STOPPED = 0x0100 # macro
PCI_PRI_STATUS_PASID = 0x8000 # macro
PCI_PRI_MAX_REQ = 0x08 # macro
PCI_PRI_ALLOC_REQ = 0x0c # macro
PCI_EXT_CAP_PRI_SIZEOF = 16 # macro
PCI_PASID_CAP = 0x04 # macro
PCI_PASID_CAP_EXEC = 0x02 # macro
PCI_PASID_CAP_PRIV = 0x04 # macro
PCI_PASID_CTRL = 0x06 # macro
PCI_PASID_CTRL_ENABLE = 0x01 # macro
PCI_PASID_CTRL_EXEC = 0x02 # macro
PCI_PASID_CTRL_PRIV = 0x04 # macro
PCI_EXT_CAP_PASID_SIZEOF = 8 # macro
PCI_SRIOV_CAP = 0x04 # macro
PCI_SRIOV_CAP_VFM = 0x00000001 # macro
def PCI_SRIOV_CAP_INTR(x):  # macro
   return ((x)>>21)
PCI_SRIOV_CTRL = 0x08 # macro
PCI_SRIOV_CTRL_VFE = 0x0001 # macro
PCI_SRIOV_CTRL_VFM = 0x0002 # macro
PCI_SRIOV_CTRL_INTR = 0x0004 # macro
PCI_SRIOV_CTRL_MSE = 0x0008 # macro
PCI_SRIOV_CTRL_ARI = 0x0010 # macro
PCI_SRIOV_STATUS = 0x0a # macro
PCI_SRIOV_STATUS_VFM = 0x0001 # macro
PCI_SRIOV_INITIAL_VF = 0x0c # macro
PCI_SRIOV_TOTAL_VF = 0x0e # macro
PCI_SRIOV_NUM_VF = 0x10 # macro
PCI_SRIOV_FUNC_LINK = 0x12 # macro
PCI_SRIOV_VF_OFFSET = 0x14 # macro
PCI_SRIOV_VF_STRIDE = 0x16 # macro
PCI_SRIOV_VF_DID = 0x1a # macro
PCI_SRIOV_SUP_PGSIZE = 0x1c # macro
PCI_SRIOV_SYS_PGSIZE = 0x20 # macro
PCI_SRIOV_BAR = 0x24 # macro
PCI_SRIOV_NUM_BARS = 6 # macro
PCI_SRIOV_VFM = 0x3c # macro
def PCI_SRIOV_VFM_BIR(x):  # macro
   return ((x)&7)
def PCI_SRIOV_VFM_OFFSET(x):  # macro
   return ((x)&~7)
PCI_SRIOV_VFM_UA = 0x0 # macro
PCI_SRIOV_VFM_MI = 0x1 # macro
PCI_SRIOV_VFM_MO = 0x2 # macro
PCI_SRIOV_VFM_AV = 0x3 # macro
PCI_EXT_CAP_SRIOV_SIZEOF = 64 # macro
PCI_LTR_MAX_SNOOP_LAT = 0x4 # macro
PCI_LTR_MAX_NOSNOOP_LAT = 0x6 # macro
PCI_LTR_VALUE_MASK = 0x000003ff # macro
PCI_LTR_SCALE_MASK = 0x00001c00 # macro
PCI_LTR_SCALE_SHIFT = 10 # macro
PCI_EXT_CAP_LTR_SIZEOF = 8 # macro
PCI_ACS_CAP = 0x04 # macro
PCI_ACS_SV = 0x0001 # macro
PCI_ACS_TB = 0x0002 # macro
PCI_ACS_RR = 0x0004 # macro
PCI_ACS_CR = 0x0008 # macro
PCI_ACS_UF = 0x0010 # macro
PCI_ACS_EC = 0x0020 # macro
PCI_ACS_DT = 0x0040 # macro
PCI_ACS_EGRESS_BITS = 0x05 # macro
PCI_ACS_CTRL = 0x06 # macro
PCI_ACS_EGRESS_CTL_V = 0x08 # macro
PCI_VSEC_HDR = 4 # macro
PCI_VSEC_HDR_LEN_SHIFT = 20 # macro
PCI_SATA_REGS = 4 # macro
PCI_SATA_REGS_MASK = 0xF # macro
PCI_SATA_REGS_INLINE = 0xF # macro
PCI_SATA_SIZEOF_SHORT = 8 # macro
PCI_SATA_SIZEOF_LONG = 16 # macro
PCI_REBAR_CAP = 4 # macro
PCI_REBAR_CAP_SIZES = 0x00FFFFF0 # macro
PCI_REBAR_CTRL = 8 # macro
PCI_REBAR_CTRL_BAR_IDX = 0x00000007 # macro
PCI_REBAR_CTRL_NBAR_MASK = 0x000000E0 # macro
PCI_REBAR_CTRL_NBAR_SHIFT = 5 # macro
PCI_REBAR_CTRL_BAR_SIZE = 0x00001F00 # macro
PCI_REBAR_CTRL_BAR_SHIFT = 8 # macro
PCI_DPA_CAP = 4 # macro
PCI_DPA_CAP_SUBSTATE_MASK = 0x1F # macro
PCI_DPA_BASE_SIZEOF = 16 # macro
PCI_TPH_CAP = 4 # macro
PCI_TPH_CAP_LOC_MASK = 0x600 # macro
PCI_TPH_LOC_NONE = 0x000 # macro
PCI_TPH_LOC_CAP = 0x200 # macro
PCI_TPH_LOC_MSIX = 0x400 # macro
PCI_TPH_CAP_ST_MASK = 0x07FF0000 # macro
PCI_TPH_CAP_ST_SHIFT = 16 # macro
PCI_TPH_BASE_SIZEOF = 12 # macro
PCI_EXP_DPC_CAP = 4 # macro
PCI_EXP_DPC_IRQ = 0x001F # macro
PCI_EXP_DPC_CAP_RP_EXT = 0x0020 # macro
PCI_EXP_DPC_CAP_POISONED_TLP = 0x0040 # macro
PCI_EXP_DPC_CAP_SW_TRIGGER = 0x0080 # macro
PCI_EXP_DPC_RP_PIO_LOG_SIZE = 0x0F00 # macro
PCI_EXP_DPC_CAP_DL_ACTIVE = 0x1000 # macro
PCI_EXP_DPC_CTL = 6 # macro
PCI_EXP_DPC_CTL_EN_FATAL = 0x0001 # macro
PCI_EXP_DPC_CTL_EN_NONFATAL = 0x0002 # macro
PCI_EXP_DPC_CTL_INT_EN = 0x0008 # macro
PCI_EXP_DPC_STATUS = 8 # macro
PCI_EXP_DPC_STATUS_TRIGGER = 0x0001 # macro
PCI_EXP_DPC_STATUS_TRIGGER_RSN = 0x0006 # macro
PCI_EXP_DPC_STATUS_INTERRUPT = 0x0008 # macro
PCI_EXP_DPC_RP_BUSY = 0x0010 # macro
PCI_EXP_DPC_STATUS_TRIGGER_RSN_EXT = 0x0060 # macro
PCI_EXP_DPC_SOURCE_ID = 10 # macro
PCI_EXP_DPC_RP_PIO_STATUS = 0x0C # macro
PCI_EXP_DPC_RP_PIO_MASK = 0x10 # macro
PCI_EXP_DPC_RP_PIO_SEVERITY = 0x14 # macro
PCI_EXP_DPC_RP_PIO_SYSERROR = 0x18 # macro
PCI_EXP_DPC_RP_PIO_EXCEPTION = 0x1C # macro
PCI_EXP_DPC_RP_PIO_HEADER_LOG = 0x20 # macro
PCI_EXP_DPC_RP_PIO_IMPSPEC_LOG = 0x30 # macro
PCI_EXP_DPC_RP_PIO_TLPPREFIX_LOG = 0x34 # macro
PCI_PTM_CAP = 0x04 # macro
PCI_PTM_CAP_REQ = 0x00000001 # macro
PCI_PTM_CAP_ROOT = 0x00000004 # macro
PCI_PTM_GRANULARITY_MASK = 0x0000FF00 # macro
PCI_PTM_CTRL = 0x08 # macro
PCI_PTM_CTRL_ENABLE = 0x00000001 # macro
PCI_PTM_CTRL_ROOT = 0x00000002 # macro
PCI_L1SS_CAP = 0x04 # macro
PCI_L1SS_CAP_PCIPM_L1_2 = 0x00000001 # macro
PCI_L1SS_CAP_PCIPM_L1_1 = 0x00000002 # macro
PCI_L1SS_CAP_ASPM_L1_2 = 0x00000004 # macro
PCI_L1SS_CAP_ASPM_L1_1 = 0x00000008 # macro
PCI_L1SS_CAP_L1_PM_SS = 0x00000010 # macro
PCI_L1SS_CAP_CM_RESTORE_TIME = 0x0000ff00 # macro
PCI_L1SS_CAP_P_PWR_ON_SCALE = 0x00030000 # macro
PCI_L1SS_CAP_P_PWR_ON_VALUE = 0x00f80000 # macro
PCI_L1SS_CTL1 = 0x08 # macro
PCI_L1SS_CTL1_PCIPM_L1_2 = 0x00000001 # macro
PCI_L1SS_CTL1_PCIPM_L1_1 = 0x00000002 # macro
PCI_L1SS_CTL1_ASPM_L1_2 = 0x00000004 # macro
PCI_L1SS_CTL1_ASPM_L1_1 = 0x00000008 # macro
PCI_L1SS_CTL1_L1_2_MASK = 0x00000005 # macro
PCI_L1SS_CTL1_L1SS_MASK = 0x0000000f # macro
PCI_L1SS_CTL1_CM_RESTORE_TIME = 0x0000ff00 # macro
PCI_L1SS_CTL1_LTR_L12_TH_VALUE = 0x03ff0000 # macro
PCI_L1SS_CTL1_LTR_L12_TH_SCALE = 0xe0000000 # macro
PCI_L1SS_CTL2 = 0x0c # macro
PCI_DVSEC_HEADER1 = 0x4 # macro
PCI_DVSEC_HEADER2 = 0x8 # macro
PCI_DLF_CAP = 0x04 # macro
PCI_DLF_EXCHANGE_ENABLE = 0x80000000 # macro
PCI_PL_16GT_LE_CTRL = 0x20 # macro
PCI_PL_16GT_LE_CTRL_DSP_TX_PRESET_MASK = 0x0000000F # macro
PCI_PL_16GT_LE_CTRL_USP_TX_PRESET_MASK = 0x000000F0 # macro
PCI_PL_16GT_LE_CTRL_USP_TX_PRESET_SHIFT = 4 # macro
struct_pci_device._pack_ = 1 # source:False
struct_pci_device._fields_ = [
    ('domain_16', ctypes.c_uint16),
    ('bus', ctypes.c_ubyte),
    ('dev', ctypes.c_ubyte),
    ('func', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
    ('vendor_id', ctypes.c_uint16),
    ('device_id', ctypes.c_uint16),
    ('subvendor_id', ctypes.c_uint16),
    ('subdevice_id', ctypes.c_uint16),
    ('PADDING_1', ctypes.c_ubyte * 2),
    ('device_class', ctypes.c_uint32),
    ('revision', ctypes.c_ubyte),
    ('PADDING_2', ctypes.c_ubyte * 3),
    ('regions', struct_pci_mem_region * 6),
    ('rom_size', ctypes.c_uint64),
    ('irq', ctypes.c_int32),
    ('PADDING_3', ctypes.c_ubyte * 4),
    ('user_data', ctypes.c_int64),
    ('vgaarb_rsrc', ctypes.c_int32),
    ('domain', ctypes.c_uint32),
]

struct_pci_agp_info._pack_ = 1 # source:False
struct_pci_agp_info._fields_ = [
    ('config_offset', ctypes.c_uint32),
    ('major_version', ctypes.c_ubyte),
    ('minor_version', ctypes.c_ubyte),
    ('rates', ctypes.c_ubyte),
    ('fast_writes', ctypes.c_uint32, 1),
    ('addr64', ctypes.c_uint32, 1),
    ('htrans', ctypes.c_uint32, 1),
    ('gart64', ctypes.c_uint32, 1),
    ('coherent', ctypes.c_uint32, 1),
    ('sideband', ctypes.c_uint32, 1),
    ('isochronus', ctypes.c_uint32, 1),
    ('PADDING_0', ctypes.c_uint8, 1),
    ('async_req_size', ctypes.c_uint32, 8),
    ('calibration_cycle_timing', ctypes.c_ubyte),
    ('max_requests', ctypes.c_ubyte),
    ('PADDING_1', ctypes.c_ubyte),
]

struct_pci_bridge_info._pack_ = 1 # source:False
struct_pci_bridge_info._fields_ = [
    ('primary_bus', ctypes.c_ubyte),
    ('secondary_bus', ctypes.c_ubyte),
    ('subordinate_bus', ctypes.c_ubyte),
    ('secondary_latency_timer', ctypes.c_ubyte),
    ('io_type', ctypes.c_ubyte),
    ('mem_type', ctypes.c_ubyte),
    ('prefetch_mem_type', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
    ('secondary_status', ctypes.c_uint16),
    ('bridge_control', ctypes.c_uint16),
    ('io_base', ctypes.c_uint32),
    ('io_limit', ctypes.c_uint32),
    ('mem_base', ctypes.c_uint32),
    ('mem_limit', ctypes.c_uint32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('prefetch_mem_base', ctypes.c_uint64),
    ('prefetch_mem_limit', ctypes.c_uint64),
]

struct_pci_pcmcia_bridge_info._pack_ = 1 # source:False
struct_pci_pcmcia_bridge_info._fields_ = [
    ('primary_bus', ctypes.c_ubyte),
    ('card_bus', ctypes.c_ubyte),
    ('subordinate_bus', ctypes.c_ubyte),
    ('cardbus_latency_timer', ctypes.c_ubyte),
    ('secondary_status', ctypes.c_uint16),
    ('bridge_control', ctypes.c_uint16),
    ('io', struct_pci_pcmcia_bridge_info_0 * 2),
    ('mem', struct_pci_pcmcia_bridge_info_1 * 2),
]

struct_pci_slot_match._pack_ = 1 # source:False
struct_pci_slot_match._fields_ = [
    ('domain', ctypes.c_uint32),
    ('bus', ctypes.c_uint32),
    ('dev', ctypes.c_uint32),
    ('func', ctypes.c_uint32),
    ('match_data', ctypes.c_int64),
]

struct_pci_id_match._pack_ = 1 # source:False
struct_pci_id_match._fields_ = [
    ('vendor_id', ctypes.c_uint32),
    ('device_id', ctypes.c_uint32),
    ('subvendor_id', ctypes.c_uint32),
    ('subdevice_id', ctypes.c_uint32),
    ('device_class', ctypes.c_uint32),
    ('device_class_mask', ctypes.c_uint32),
    ('match_data', ctypes.c_int64),
]

__all__ = \
    ['HT_3BIT_CAP_MASK', 'HT_5BIT_CAP_MASK',
    'HT_CAPTYPE_DIRECT_ROUTE', 'HT_CAPTYPE_ERROR_RETRY',
    'HT_CAPTYPE_EXTCONF', 'HT_CAPTYPE_GEN3', 'HT_CAPTYPE_HOST',
    'HT_CAPTYPE_IRQ', 'HT_CAPTYPE_MSI_MAPPING', 'HT_CAPTYPE_PM',
    'HT_CAPTYPE_REMAPPING_40', 'HT_CAPTYPE_REMAPPING_64',
    'HT_CAPTYPE_SLAVE', 'HT_CAPTYPE_UNITID_CLUMP', 'HT_CAPTYPE_VCSET',
    'HT_CAP_SIZEOF_LONG', 'HT_CAP_SIZEOF_SHORT', 'HT_MSI_ADDR_HI',
    'HT_MSI_ADDR_LO', 'HT_MSI_ADDR_LO_MASK', 'HT_MSI_FIXED_ADDR',
    'HT_MSI_FLAGS', 'HT_MSI_FLAGS_ENABLE', 'HT_MSI_FLAGS_FIXED',
    'LINUX_PCI_REGS_H', 'PCIACCESS_H', 'PCI_ACS_CAP', 'PCI_ACS_CR',
    'PCI_ACS_CTRL', 'PCI_ACS_DT', 'PCI_ACS_EC', 'PCI_ACS_EGRESS_BITS',
    'PCI_ACS_EGRESS_CTL_V', 'PCI_ACS_RR', 'PCI_ACS_SV', 'PCI_ACS_TB',
    'PCI_ACS_UF', 'PCI_AF_CAP', 'PCI_AF_CAP_FLR', 'PCI_AF_CAP_TP',
    'PCI_AF_CTRL', 'PCI_AF_CTRL_FLR', 'PCI_AF_LENGTH',
    'PCI_AF_STATUS', 'PCI_AF_STATUS_TP', 'PCI_AGP_COMMAND',
    'PCI_AGP_COMMAND_64BIT', 'PCI_AGP_COMMAND_AGP',
    'PCI_AGP_COMMAND_FW', 'PCI_AGP_COMMAND_RATE1',
    'PCI_AGP_COMMAND_RATE2', 'PCI_AGP_COMMAND_RATE4',
    'PCI_AGP_COMMAND_RQ_MASK', 'PCI_AGP_COMMAND_SBA', 'PCI_AGP_RFU',
    'PCI_AGP_SIZEOF', 'PCI_AGP_STATUS', 'PCI_AGP_STATUS_64BIT',
    'PCI_AGP_STATUS_FW', 'PCI_AGP_STATUS_RATE1',
    'PCI_AGP_STATUS_RATE2', 'PCI_AGP_STATUS_RATE4',
    'PCI_AGP_STATUS_RQ_MASK', 'PCI_AGP_STATUS_SBA', 'PCI_AGP_VERSION',
    'PCI_ARI_CAP', 'PCI_ARI_CAP_ACS', 'PCI_ARI_CAP_MFVC',
    'PCI_ARI_CTRL', 'PCI_ARI_CTRL_ACS', 'PCI_ARI_CTRL_MFVC',
    'PCI_ATS_CAP', 'PCI_ATS_CAP_PAGE_ALIGNED', 'PCI_ATS_CTRL',
    'PCI_ATS_CTRL_ENABLE', 'PCI_ATS_MAX_QDEP', 'PCI_ATS_MIN_STU',
    'PCI_BASE_ADDRESS_0', 'PCI_BASE_ADDRESS_1', 'PCI_BASE_ADDRESS_2',
    'PCI_BASE_ADDRESS_3', 'PCI_BASE_ADDRESS_4', 'PCI_BASE_ADDRESS_5',
    'PCI_BASE_ADDRESS_IO_MASK', 'PCI_BASE_ADDRESS_MEM_MASK',
    'PCI_BASE_ADDRESS_MEM_PREFETCH', 'PCI_BASE_ADDRESS_MEM_TYPE_1M',
    'PCI_BASE_ADDRESS_MEM_TYPE_32', 'PCI_BASE_ADDRESS_MEM_TYPE_64',
    'PCI_BASE_ADDRESS_MEM_TYPE_MASK', 'PCI_BASE_ADDRESS_SPACE',
    'PCI_BASE_ADDRESS_SPACE_IO', 'PCI_BASE_ADDRESS_SPACE_MEMORY',
    'PCI_BIST', 'PCI_BIST_CAPABLE', 'PCI_BIST_CODE_MASK',
    'PCI_BIST_START', 'PCI_BRIDGE_CONTROL',
    'PCI_BRIDGE_CTL_BUS_RESET', 'PCI_BRIDGE_CTL_FAST_BACK',
    'PCI_BRIDGE_CTL_ISA', 'PCI_BRIDGE_CTL_MASTER_ABORT',
    'PCI_BRIDGE_CTL_PARITY', 'PCI_BRIDGE_CTL_SERR',
    'PCI_BRIDGE_CTL_VGA', 'PCI_CACHE_LINE_SIZE',
    'PCI_CAPABILITY_LIST', 'PCI_CAP_AF_SIZEOF',
    'PCI_CAP_EXP_ENDPOINT_SIZEOF_V1',
    'PCI_CAP_EXP_ENDPOINT_SIZEOF_V2',
    'PCI_CAP_EXP_RC_ENDPOINT_SIZEOF_V1',
    'PCI_CAP_EXP_RC_ENDPOINT_SIZEOF_V2', 'PCI_CAP_FLAGS',
    'PCI_CAP_ID_AF', 'PCI_CAP_ID_AGP', 'PCI_CAP_ID_AGP3',
    'PCI_CAP_ID_CCRC', 'PCI_CAP_ID_CHSWP', 'PCI_CAP_ID_DBG',
    'PCI_CAP_ID_EA', 'PCI_CAP_ID_EXP', 'PCI_CAP_ID_HT',
    'PCI_CAP_ID_MAX', 'PCI_CAP_ID_MSI', 'PCI_CAP_ID_MSIX',
    'PCI_CAP_ID_PCIX', 'PCI_CAP_ID_PM', 'PCI_CAP_ID_SATA',
    'PCI_CAP_ID_SECDEV', 'PCI_CAP_ID_SHPC', 'PCI_CAP_ID_SLOTID',
    'PCI_CAP_ID_SSVID', 'PCI_CAP_ID_VNDR', 'PCI_CAP_ID_VPD',
    'PCI_CAP_LIST_ID', 'PCI_CAP_LIST_NEXT', 'PCI_CAP_MSIX_SIZEOF',
    'PCI_CAP_PCIX_SIZEOF_V0', 'PCI_CAP_PCIX_SIZEOF_V1',
    'PCI_CAP_PCIX_SIZEOF_V2', 'PCI_CAP_SIZEOF',
    'PCI_CAP_VC_BASE_SIZEOF', 'PCI_CAP_VC_PER_VC_SIZEOF',
    'PCI_CAP_VPD_SIZEOF', 'PCI_CARDBUS_CIS', 'PCI_CB_BRIDGE_CONTROL',
    'PCI_CB_BRIDGE_CTL_16BIT_INT', 'PCI_CB_BRIDGE_CTL_CB_RESET',
    'PCI_CB_BRIDGE_CTL_ISA', 'PCI_CB_BRIDGE_CTL_MASTER_ABORT',
    'PCI_CB_BRIDGE_CTL_PARITY', 'PCI_CB_BRIDGE_CTL_POST_WRITES',
    'PCI_CB_BRIDGE_CTL_PREFETCH_MEM0',
    'PCI_CB_BRIDGE_CTL_PREFETCH_MEM1', 'PCI_CB_BRIDGE_CTL_SERR',
    'PCI_CB_BRIDGE_CTL_VGA', 'PCI_CB_CAPABILITY_LIST',
    'PCI_CB_CARD_BUS', 'PCI_CB_IO_BASE_0', 'PCI_CB_IO_BASE_0_HI',
    'PCI_CB_IO_BASE_1', 'PCI_CB_IO_BASE_1_HI', 'PCI_CB_IO_LIMIT_0',
    'PCI_CB_IO_LIMIT_0_HI', 'PCI_CB_IO_LIMIT_1',
    'PCI_CB_IO_LIMIT_1_HI', 'PCI_CB_IO_RANGE_MASK',
    'PCI_CB_LATENCY_TIMER', 'PCI_CB_LEGACY_MODE_BASE',
    'PCI_CB_MEMORY_BASE_0', 'PCI_CB_MEMORY_BASE_1',
    'PCI_CB_MEMORY_LIMIT_0', 'PCI_CB_MEMORY_LIMIT_1',
    'PCI_CB_PRIMARY_BUS', 'PCI_CB_SEC_STATUS',
    'PCI_CB_SUBORDINATE_BUS', 'PCI_CB_SUBSYSTEM_ID',
    'PCI_CB_SUBSYSTEM_VENDOR_ID', 'PCI_CFG_SPACE_EXP_SIZE',
    'PCI_CFG_SPACE_SIZE', 'PCI_CHSWP_CSR', 'PCI_CHSWP_DHA',
    'PCI_CHSWP_EIM', 'PCI_CHSWP_EXT', 'PCI_CHSWP_INS',
    'PCI_CHSWP_LOO', 'PCI_CHSWP_PI', 'PCI_CHSWP_PIE',
    'PCI_CLASS_DEVICE', 'PCI_CLASS_PROG', 'PCI_CLASS_REVISION',
    'PCI_COMMAND', 'PCI_COMMAND_FAST_BACK',
    'PCI_COMMAND_INTX_DISABLE', 'PCI_COMMAND_INVALIDATE',
    'PCI_COMMAND_IO', 'PCI_COMMAND_MASTER', 'PCI_COMMAND_MEMORY',
    'PCI_COMMAND_PARITY', 'PCI_COMMAND_SERR', 'PCI_COMMAND_SPECIAL',
    'PCI_COMMAND_VGA_PALETTE', 'PCI_COMMAND_WAIT', 'PCI_DEVICE_ID',
    'PCI_DEV_MAP_FLAG_CACHABLE', 'PCI_DEV_MAP_FLAG_WRITABLE',
    'PCI_DEV_MAP_FLAG_WRITE_COMBINE', 'PCI_DLF_CAP',
    'PCI_DLF_EXCHANGE_ENABLE', 'PCI_DPA_BASE_SIZEOF', 'PCI_DPA_CAP',
    'PCI_DPA_CAP_SUBSTATE_MASK', 'PCI_DVSEC_HEADER1',
    'PCI_DVSEC_HEADER2', 'PCI_EA_BASE', 'PCI_EA_BEI',
    'PCI_EA_BEI_BAR0', 'PCI_EA_BEI_BAR5', 'PCI_EA_BEI_BRIDGE',
    'PCI_EA_BEI_ENI', 'PCI_EA_BEI_RESERVED', 'PCI_EA_BEI_ROM',
    'PCI_EA_BEI_VF_BAR0', 'PCI_EA_BEI_VF_BAR5', 'PCI_EA_ENABLE',
    'PCI_EA_ES', 'PCI_EA_FIELD_MASK', 'PCI_EA_FIRST_ENT',
    'PCI_EA_FIRST_ENT_BRIDGE', 'PCI_EA_IS_64', 'PCI_EA_MAX_OFFSET',
    'PCI_EA_NUM_ENT', 'PCI_EA_NUM_ENT_MASK', 'PCI_EA_PP',
    'PCI_EA_P_BRIDGE_IO', 'PCI_EA_P_BRIDGE_MEM',
    'PCI_EA_P_BRIDGE_MEM_PREFETCH', 'PCI_EA_P_IO',
    'PCI_EA_P_IO_RESERVED', 'PCI_EA_P_MEM', 'PCI_EA_P_MEM_PREFETCH',
    'PCI_EA_P_MEM_RESERVED', 'PCI_EA_P_UNAVAILABLE',
    'PCI_EA_P_VF_MEM', 'PCI_EA_P_VF_MEM_PREFETCH',
    'PCI_EA_SEC_BUS_MASK', 'PCI_EA_SP', 'PCI_EA_SUB_BUS_MASK',
    'PCI_EA_SUB_BUS_SHIFT', 'PCI_EA_WRITABLE', 'PCI_ERR_CAP',
    'PCI_ERR_CAP_ECRC_CHKC', 'PCI_ERR_CAP_ECRC_CHKE',
    'PCI_ERR_CAP_ECRC_GENC', 'PCI_ERR_CAP_ECRC_GENE',
    'PCI_ERR_COR_ADV_NFAT', 'PCI_ERR_COR_BAD_DLLP',
    'PCI_ERR_COR_BAD_TLP', 'PCI_ERR_COR_INTERNAL',
    'PCI_ERR_COR_LOG_OVER', 'PCI_ERR_COR_MASK', 'PCI_ERR_COR_RCVR',
    'PCI_ERR_COR_REP_ROLL', 'PCI_ERR_COR_REP_TIMER',
    'PCI_ERR_COR_STATUS', 'PCI_ERR_HEADER_LOG',
    'PCI_ERR_ROOT_AER_IRQ', 'PCI_ERR_ROOT_CMD_COR_EN',
    'PCI_ERR_ROOT_CMD_FATAL_EN', 'PCI_ERR_ROOT_CMD_NONFATAL_EN',
    'PCI_ERR_ROOT_COMMAND', 'PCI_ERR_ROOT_COR_RCV',
    'PCI_ERR_ROOT_ERR_SRC', 'PCI_ERR_ROOT_FATAL_RCV',
    'PCI_ERR_ROOT_FIRST_FATAL', 'PCI_ERR_ROOT_MULTI_COR_RCV',
    'PCI_ERR_ROOT_MULTI_UNCOR_RCV', 'PCI_ERR_ROOT_NONFATAL_RCV',
    'PCI_ERR_ROOT_STATUS', 'PCI_ERR_ROOT_UNCOR_RCV',
    'PCI_ERR_UNCOR_MASK', 'PCI_ERR_UNCOR_SEVER',
    'PCI_ERR_UNCOR_STATUS', 'PCI_ERR_UNC_ACSV', 'PCI_ERR_UNC_ATOMEG',
    'PCI_ERR_UNC_COMP_ABORT', 'PCI_ERR_UNC_COMP_TIME',
    'PCI_ERR_UNC_DLP', 'PCI_ERR_UNC_ECRC', 'PCI_ERR_UNC_FCP',
    'PCI_ERR_UNC_INTN', 'PCI_ERR_UNC_MALF_TLP', 'PCI_ERR_UNC_MCBTLP',
    'PCI_ERR_UNC_POISON_TLP', 'PCI_ERR_UNC_RX_OVER',
    'PCI_ERR_UNC_SURPDN', 'PCI_ERR_UNC_TLPPRE', 'PCI_ERR_UNC_UND',
    'PCI_ERR_UNC_UNSUP', 'PCI_ERR_UNC_UNX_COMP', 'PCI_EXP_DEVCAP',
    'PCI_EXP_DEVCAP2', 'PCI_EXP_DEVCAP2_ARI',
    'PCI_EXP_DEVCAP2_ATOMIC_COMP128', 'PCI_EXP_DEVCAP2_ATOMIC_COMP32',
    'PCI_EXP_DEVCAP2_ATOMIC_COMP64', 'PCI_EXP_DEVCAP2_ATOMIC_ROUTE',
    'PCI_EXP_DEVCAP2_COMP_TMOUT_DIS', 'PCI_EXP_DEVCAP2_EE_PREFIX',
    'PCI_EXP_DEVCAP2_LTR', 'PCI_EXP_DEVCAP2_OBFF_MASK',
    'PCI_EXP_DEVCAP2_OBFF_MSG', 'PCI_EXP_DEVCAP2_OBFF_WAKE',
    'PCI_EXP_DEVCAP_ATN_BUT', 'PCI_EXP_DEVCAP_ATN_IND',
    'PCI_EXP_DEVCAP_EXT_TAG', 'PCI_EXP_DEVCAP_FLR',
    'PCI_EXP_DEVCAP_L0S', 'PCI_EXP_DEVCAP_L1',
    'PCI_EXP_DEVCAP_PAYLOAD', 'PCI_EXP_DEVCAP_PHANTOM',
    'PCI_EXP_DEVCAP_PWR_IND', 'PCI_EXP_DEVCAP_PWR_SCL',
    'PCI_EXP_DEVCAP_PWR_VAL', 'PCI_EXP_DEVCAP_RBER', 'PCI_EXP_DEVCTL',
    'PCI_EXP_DEVCTL2', 'PCI_EXP_DEVCTL2_ARI',
    'PCI_EXP_DEVCTL2_ATOMIC_EGRESS_BLOCK',
    'PCI_EXP_DEVCTL2_ATOMIC_REQ', 'PCI_EXP_DEVCTL2_COMP_TIMEOUT',
    'PCI_EXP_DEVCTL2_COMP_TMOUT_DIS', 'PCI_EXP_DEVCTL2_IDO_CMP_EN',
    'PCI_EXP_DEVCTL2_IDO_REQ_EN', 'PCI_EXP_DEVCTL2_LTR_EN',
    'PCI_EXP_DEVCTL2_OBFF_MSGA_EN', 'PCI_EXP_DEVCTL2_OBFF_MSGB_EN',
    'PCI_EXP_DEVCTL2_OBFF_WAKE_EN', 'PCI_EXP_DEVCTL_AUX_PME',
    'PCI_EXP_DEVCTL_BCR_FLR', 'PCI_EXP_DEVCTL_CERE',
    'PCI_EXP_DEVCTL_EXT_TAG', 'PCI_EXP_DEVCTL_FERE',
    'PCI_EXP_DEVCTL_NFERE', 'PCI_EXP_DEVCTL_NOSNOOP_EN',
    'PCI_EXP_DEVCTL_PAYLOAD', 'PCI_EXP_DEVCTL_PAYLOAD_1024B',
    'PCI_EXP_DEVCTL_PAYLOAD_128B', 'PCI_EXP_DEVCTL_PAYLOAD_2048B',
    'PCI_EXP_DEVCTL_PAYLOAD_256B', 'PCI_EXP_DEVCTL_PAYLOAD_4096B',
    'PCI_EXP_DEVCTL_PAYLOAD_512B', 'PCI_EXP_DEVCTL_PHANTOM',
    'PCI_EXP_DEVCTL_READRQ', 'PCI_EXP_DEVCTL_READRQ_1024B',
    'PCI_EXP_DEVCTL_READRQ_128B', 'PCI_EXP_DEVCTL_READRQ_2048B',
    'PCI_EXP_DEVCTL_READRQ_256B', 'PCI_EXP_DEVCTL_READRQ_4096B',
    'PCI_EXP_DEVCTL_READRQ_512B', 'PCI_EXP_DEVCTL_RELAX_EN',
    'PCI_EXP_DEVCTL_URRE', 'PCI_EXP_DEVSTA', 'PCI_EXP_DEVSTA2',
    'PCI_EXP_DEVSTA_AUXPD', 'PCI_EXP_DEVSTA_CED',
    'PCI_EXP_DEVSTA_FED', 'PCI_EXP_DEVSTA_NFED',
    'PCI_EXP_DEVSTA_TRPND', 'PCI_EXP_DEVSTA_URD', 'PCI_EXP_DPC_CAP',
    'PCI_EXP_DPC_CAP_DL_ACTIVE', 'PCI_EXP_DPC_CAP_POISONED_TLP',
    'PCI_EXP_DPC_CAP_RP_EXT', 'PCI_EXP_DPC_CAP_SW_TRIGGER',
    'PCI_EXP_DPC_CTL', 'PCI_EXP_DPC_CTL_EN_FATAL',
    'PCI_EXP_DPC_CTL_EN_NONFATAL', 'PCI_EXP_DPC_CTL_INT_EN',
    'PCI_EXP_DPC_IRQ', 'PCI_EXP_DPC_RP_BUSY',
    'PCI_EXP_DPC_RP_PIO_EXCEPTION', 'PCI_EXP_DPC_RP_PIO_HEADER_LOG',
    'PCI_EXP_DPC_RP_PIO_IMPSPEC_LOG', 'PCI_EXP_DPC_RP_PIO_LOG_SIZE',
    'PCI_EXP_DPC_RP_PIO_MASK', 'PCI_EXP_DPC_RP_PIO_SEVERITY',
    'PCI_EXP_DPC_RP_PIO_STATUS', 'PCI_EXP_DPC_RP_PIO_SYSERROR',
    'PCI_EXP_DPC_RP_PIO_TLPPREFIX_LOG', 'PCI_EXP_DPC_SOURCE_ID',
    'PCI_EXP_DPC_STATUS', 'PCI_EXP_DPC_STATUS_INTERRUPT',
    'PCI_EXP_DPC_STATUS_TRIGGER', 'PCI_EXP_DPC_STATUS_TRIGGER_RSN',
    'PCI_EXP_DPC_STATUS_TRIGGER_RSN_EXT', 'PCI_EXP_FLAGS',
    'PCI_EXP_FLAGS_IRQ', 'PCI_EXP_FLAGS_SLOT', 'PCI_EXP_FLAGS_TYPE',
    'PCI_EXP_FLAGS_VERS', 'PCI_EXP_LNKCAP', 'PCI_EXP_LNKCAP2',
    'PCI_EXP_LNKCAP2_CROSSLINK', 'PCI_EXP_LNKCAP2_SLS_16_0GB',
    'PCI_EXP_LNKCAP2_SLS_2_5GB', 'PCI_EXP_LNKCAP2_SLS_32_0GB',
    'PCI_EXP_LNKCAP2_SLS_5_0GB', 'PCI_EXP_LNKCAP2_SLS_64_0GB',
    'PCI_EXP_LNKCAP2_SLS_8_0GB', 'PCI_EXP_LNKCAP_ASPMS',
    'PCI_EXP_LNKCAP_ASPM_L0S', 'PCI_EXP_LNKCAP_ASPM_L1',
    'PCI_EXP_LNKCAP_CLKPM', 'PCI_EXP_LNKCAP_DLLLARC',
    'PCI_EXP_LNKCAP_L0SEL', 'PCI_EXP_LNKCAP_L1EL',
    'PCI_EXP_LNKCAP_LBNC', 'PCI_EXP_LNKCAP_MLW', 'PCI_EXP_LNKCAP_PN',
    'PCI_EXP_LNKCAP_SDERC', 'PCI_EXP_LNKCAP_SLS',
    'PCI_EXP_LNKCAP_SLS_16_0GB', 'PCI_EXP_LNKCAP_SLS_2_5GB',
    'PCI_EXP_LNKCAP_SLS_32_0GB', 'PCI_EXP_LNKCAP_SLS_5_0GB',
    'PCI_EXP_LNKCAP_SLS_64_0GB', 'PCI_EXP_LNKCAP_SLS_8_0GB',
    'PCI_EXP_LNKCTL', 'PCI_EXP_LNKCTL2', 'PCI_EXP_LNKCTL2_ENTER_COMP',
    'PCI_EXP_LNKCTL2_HASD', 'PCI_EXP_LNKCTL2_TLS',
    'PCI_EXP_LNKCTL2_TLS_16_0GT', 'PCI_EXP_LNKCTL2_TLS_2_5GT',
    'PCI_EXP_LNKCTL2_TLS_32_0GT', 'PCI_EXP_LNKCTL2_TLS_5_0GT',
    'PCI_EXP_LNKCTL2_TLS_64_0GT', 'PCI_EXP_LNKCTL2_TLS_8_0GT',
    'PCI_EXP_LNKCTL2_TX_MARGIN', 'PCI_EXP_LNKCTL_ASPMC',
    'PCI_EXP_LNKCTL_ASPM_L0S', 'PCI_EXP_LNKCTL_ASPM_L1',
    'PCI_EXP_LNKCTL_CCC', 'PCI_EXP_LNKCTL_CLKREQ_EN',
    'PCI_EXP_LNKCTL_ES', 'PCI_EXP_LNKCTL_HAWD',
    'PCI_EXP_LNKCTL_LABIE', 'PCI_EXP_LNKCTL_LBMIE',
    'PCI_EXP_LNKCTL_LD', 'PCI_EXP_LNKCTL_RCB', 'PCI_EXP_LNKCTL_RL',
    'PCI_EXP_LNKSTA', 'PCI_EXP_LNKSTA2', 'PCI_EXP_LNKSTA_CLS',
    'PCI_EXP_LNKSTA_CLS_16_0GB', 'PCI_EXP_LNKSTA_CLS_2_5GB',
    'PCI_EXP_LNKSTA_CLS_32_0GB', 'PCI_EXP_LNKSTA_CLS_5_0GB',
    'PCI_EXP_LNKSTA_CLS_64_0GB', 'PCI_EXP_LNKSTA_CLS_8_0GB',
    'PCI_EXP_LNKSTA_DLLLA', 'PCI_EXP_LNKSTA_LABS',
    'PCI_EXP_LNKSTA_LBMS', 'PCI_EXP_LNKSTA_LT', 'PCI_EXP_LNKSTA_NLW',
    'PCI_EXP_LNKSTA_NLW_SHIFT', 'PCI_EXP_LNKSTA_NLW_X1',
    'PCI_EXP_LNKSTA_NLW_X2', 'PCI_EXP_LNKSTA_NLW_X4',
    'PCI_EXP_LNKSTA_NLW_X8', 'PCI_EXP_LNKSTA_SLC', 'PCI_EXP_RTCAP',
    'PCI_EXP_RTCAP_CRSVIS', 'PCI_EXP_RTCTL', 'PCI_EXP_RTCTL_CRSSVE',
    'PCI_EXP_RTCTL_PMEIE', 'PCI_EXP_RTCTL_SECEE',
    'PCI_EXP_RTCTL_SEFEE', 'PCI_EXP_RTCTL_SENFEE', 'PCI_EXP_RTSTA',
    'PCI_EXP_RTSTA_PENDING', 'PCI_EXP_RTSTA_PME', 'PCI_EXP_SLTCAP',
    'PCI_EXP_SLTCAP2', 'PCI_EXP_SLTCAP2_IBPD', 'PCI_EXP_SLTCAP_ABP',
    'PCI_EXP_SLTCAP_AIP', 'PCI_EXP_SLTCAP_EIP', 'PCI_EXP_SLTCAP_HPC',
    'PCI_EXP_SLTCAP_HPS', 'PCI_EXP_SLTCAP_MRLSP',
    'PCI_EXP_SLTCAP_NCCS', 'PCI_EXP_SLTCAP_PCP', 'PCI_EXP_SLTCAP_PIP',
    'PCI_EXP_SLTCAP_PSN', 'PCI_EXP_SLTCAP_SPLS',
    'PCI_EXP_SLTCAP_SPLV', 'PCI_EXP_SLTCTL', 'PCI_EXP_SLTCTL2',
    'PCI_EXP_SLTCTL_ABPE', 'PCI_EXP_SLTCTL_AIC',
    'PCI_EXP_SLTCTL_ATTN_IND_BLINK', 'PCI_EXP_SLTCTL_ATTN_IND_OFF',
    'PCI_EXP_SLTCTL_ATTN_IND_ON', 'PCI_EXP_SLTCTL_ATTN_IND_SHIFT',
    'PCI_EXP_SLTCTL_CCIE', 'PCI_EXP_SLTCTL_DLLSCE',
    'PCI_EXP_SLTCTL_EIC', 'PCI_EXP_SLTCTL_HPIE',
    'PCI_EXP_SLTCTL_IBPD_DISABLE', 'PCI_EXP_SLTCTL_MRLSCE',
    'PCI_EXP_SLTCTL_PCC', 'PCI_EXP_SLTCTL_PDCE',
    'PCI_EXP_SLTCTL_PFDE', 'PCI_EXP_SLTCTL_PIC',
    'PCI_EXP_SLTCTL_PWR_IND_BLINK', 'PCI_EXP_SLTCTL_PWR_IND_OFF',
    'PCI_EXP_SLTCTL_PWR_IND_ON', 'PCI_EXP_SLTCTL_PWR_OFF',
    'PCI_EXP_SLTCTL_PWR_ON', 'PCI_EXP_SLTSTA', 'PCI_EXP_SLTSTA2',
    'PCI_EXP_SLTSTA_ABP', 'PCI_EXP_SLTSTA_CC', 'PCI_EXP_SLTSTA_DLLSC',
    'PCI_EXP_SLTSTA_EIS', 'PCI_EXP_SLTSTA_MRLSC',
    'PCI_EXP_SLTSTA_MRLSS', 'PCI_EXP_SLTSTA_PDC',
    'PCI_EXP_SLTSTA_PDS', 'PCI_EXP_SLTSTA_PFD',
    'PCI_EXP_TYPE_DOWNSTREAM', 'PCI_EXP_TYPE_ENDPOINT',
    'PCI_EXP_TYPE_LEG_END', 'PCI_EXP_TYPE_PCIE_BRIDGE',
    'PCI_EXP_TYPE_PCI_BRIDGE', 'PCI_EXP_TYPE_RC_EC',
    'PCI_EXP_TYPE_RC_END', 'PCI_EXP_TYPE_ROOT_PORT',
    'PCI_EXP_TYPE_UPSTREAM', 'PCI_EXT_CAP_ARI_SIZEOF',
    'PCI_EXT_CAP_ATS_SIZEOF', 'PCI_EXT_CAP_DSN_SIZEOF',
    'PCI_EXT_CAP_ID_ACS', 'PCI_EXT_CAP_ID_AMD_XXX',
    'PCI_EXT_CAP_ID_ARI', 'PCI_EXT_CAP_ID_ATS', 'PCI_EXT_CAP_ID_CAC',
    'PCI_EXT_CAP_ID_DLF', 'PCI_EXT_CAP_ID_DPA', 'PCI_EXT_CAP_ID_DPC',
    'PCI_EXT_CAP_ID_DSN', 'PCI_EXT_CAP_ID_DVSEC',
    'PCI_EXT_CAP_ID_ERR', 'PCI_EXT_CAP_ID_L1SS', 'PCI_EXT_CAP_ID_LTR',
    'PCI_EXT_CAP_ID_MAX', 'PCI_EXT_CAP_ID_MCAST',
    'PCI_EXT_CAP_ID_MFVC', 'PCI_EXT_CAP_ID_MRIOV',
    'PCI_EXT_CAP_ID_PASID', 'PCI_EXT_CAP_ID_PL_16GT',
    'PCI_EXT_CAP_ID_PMUX', 'PCI_EXT_CAP_ID_PRI', 'PCI_EXT_CAP_ID_PTM',
    'PCI_EXT_CAP_ID_PWR', 'PCI_EXT_CAP_ID_RCEC',
    'PCI_EXT_CAP_ID_RCILC', 'PCI_EXT_CAP_ID_RCLD',
    'PCI_EXT_CAP_ID_RCRB', 'PCI_EXT_CAP_ID_REBAR',
    'PCI_EXT_CAP_ID_SECPCI', 'PCI_EXT_CAP_ID_SRIOV',
    'PCI_EXT_CAP_ID_TPH', 'PCI_EXT_CAP_ID_VC', 'PCI_EXT_CAP_ID_VC9',
    'PCI_EXT_CAP_ID_VNDR', 'PCI_EXT_CAP_LTR_SIZEOF',
    'PCI_EXT_CAP_MCAST_ENDPOINT_SIZEOF', 'PCI_EXT_CAP_PASID_SIZEOF',
    'PCI_EXT_CAP_PRI_SIZEOF', 'PCI_EXT_CAP_PWR_SIZEOF',
    'PCI_EXT_CAP_SRIOV_SIZEOF', 'PCI_HEADER_TYPE',
    'PCI_HEADER_TYPE_BRIDGE', 'PCI_HEADER_TYPE_CARDBUS',
    'PCI_HEADER_TYPE_MASK', 'PCI_HEADER_TYPE_NORMAL',
    'PCI_INTERRUPT_LINE', 'PCI_INTERRUPT_PIN', 'PCI_IO_1K_RANGE_MASK',
    'PCI_IO_BASE', 'PCI_IO_BASE_UPPER16', 'PCI_IO_LIMIT',
    'PCI_IO_LIMIT_UPPER16', 'PCI_IO_RANGE_MASK',
    'PCI_IO_RANGE_TYPE_16', 'PCI_IO_RANGE_TYPE_32',
    'PCI_IO_RANGE_TYPE_MASK', 'PCI_L1SS_CAP',
    'PCI_L1SS_CAP_ASPM_L1_1', 'PCI_L1SS_CAP_ASPM_L1_2',
    'PCI_L1SS_CAP_CM_RESTORE_TIME', 'PCI_L1SS_CAP_L1_PM_SS',
    'PCI_L1SS_CAP_PCIPM_L1_1', 'PCI_L1SS_CAP_PCIPM_L1_2',
    'PCI_L1SS_CAP_P_PWR_ON_SCALE', 'PCI_L1SS_CAP_P_PWR_ON_VALUE',
    'PCI_L1SS_CTL1', 'PCI_L1SS_CTL1_ASPM_L1_1',
    'PCI_L1SS_CTL1_ASPM_L1_2', 'PCI_L1SS_CTL1_CM_RESTORE_TIME',
    'PCI_L1SS_CTL1_L1SS_MASK', 'PCI_L1SS_CTL1_L1_2_MASK',
    'PCI_L1SS_CTL1_LTR_L12_TH_SCALE',
    'PCI_L1SS_CTL1_LTR_L12_TH_VALUE', 'PCI_L1SS_CTL1_PCIPM_L1_1',
    'PCI_L1SS_CTL1_PCIPM_L1_2', 'PCI_L1SS_CTL2', 'PCI_LATENCY_TIMER',
    'PCI_LTR_MAX_NOSNOOP_LAT', 'PCI_LTR_MAX_SNOOP_LAT',
    'PCI_LTR_SCALE_MASK', 'PCI_LTR_SCALE_SHIFT', 'PCI_LTR_VALUE_MASK',
    'PCI_MATCH_ANY', 'PCI_MAX_LAT', 'PCI_MEMORY_BASE',
    'PCI_MEMORY_LIMIT', 'PCI_MEMORY_RANGE_MASK',
    'PCI_MEMORY_RANGE_TYPE_MASK', 'PCI_MIN_GNT',
    'PCI_MSIX_ENTRY_CTRL_MASKBIT', 'PCI_MSIX_ENTRY_DATA',
    'PCI_MSIX_ENTRY_LOWER_ADDR', 'PCI_MSIX_ENTRY_SIZE',
    'PCI_MSIX_ENTRY_UPPER_ADDR', 'PCI_MSIX_ENTRY_VECTOR_CTRL',
    'PCI_MSIX_FLAGS', 'PCI_MSIX_FLAGS_BIRMASK',
    'PCI_MSIX_FLAGS_ENABLE', 'PCI_MSIX_FLAGS_MASKALL',
    'PCI_MSIX_FLAGS_QSIZE', 'PCI_MSIX_PBA', 'PCI_MSIX_PBA_BIR',
    'PCI_MSIX_PBA_OFFSET', 'PCI_MSIX_TABLE', 'PCI_MSIX_TABLE_BIR',
    'PCI_MSIX_TABLE_OFFSET', 'PCI_MSI_ADDRESS_HI',
    'PCI_MSI_ADDRESS_LO', 'PCI_MSI_DATA_32', 'PCI_MSI_DATA_64',
    'PCI_MSI_FLAGS', 'PCI_MSI_FLAGS_64BIT', 'PCI_MSI_FLAGS_ENABLE',
    'PCI_MSI_FLAGS_MASKBIT', 'PCI_MSI_FLAGS_QMASK',
    'PCI_MSI_FLAGS_QSIZE', 'PCI_MSI_MASK_32', 'PCI_MSI_MASK_64',
    'PCI_MSI_PENDING_32', 'PCI_MSI_PENDING_64', 'PCI_MSI_RFU',
    'PCI_PASID_CAP', 'PCI_PASID_CAP_EXEC', 'PCI_PASID_CAP_PRIV',
    'PCI_PASID_CTRL', 'PCI_PASID_CTRL_ENABLE', 'PCI_PASID_CTRL_EXEC',
    'PCI_PASID_CTRL_PRIV', 'PCI_PL_16GT_LE_CTRL',
    'PCI_PL_16GT_LE_CTRL_DSP_TX_PRESET_MASK',
    'PCI_PL_16GT_LE_CTRL_USP_TX_PRESET_MASK',
    'PCI_PL_16GT_LE_CTRL_USP_TX_PRESET_SHIFT', 'PCI_PM_BPCC_ENABLE',
    'PCI_PM_CAP_AUX_POWER', 'PCI_PM_CAP_D1', 'PCI_PM_CAP_D2',
    'PCI_PM_CAP_DSI', 'PCI_PM_CAP_PME', 'PCI_PM_CAP_PME_CLOCK',
    'PCI_PM_CAP_PME_D0', 'PCI_PM_CAP_PME_D1', 'PCI_PM_CAP_PME_D2',
    'PCI_PM_CAP_PME_D3cold', 'PCI_PM_CAP_PME_D3hot',
    'PCI_PM_CAP_PME_MASK', 'PCI_PM_CAP_PME_SHIFT',
    'PCI_PM_CAP_RESERVED', 'PCI_PM_CAP_VER_MASK', 'PCI_PM_CTRL',
    'PCI_PM_CTRL_DATA_SCALE_MASK', 'PCI_PM_CTRL_DATA_SEL_MASK',
    'PCI_PM_CTRL_NO_SOFT_RESET', 'PCI_PM_CTRL_PME_ENABLE',
    'PCI_PM_CTRL_PME_STATUS', 'PCI_PM_CTRL_STATE_MASK',
    'PCI_PM_DATA_REGISTER', 'PCI_PM_PMC', 'PCI_PM_PPB_B2_B3',
    'PCI_PM_PPB_EXTENSIONS', 'PCI_PM_SIZEOF', 'PCI_PREF_BASE_UPPER32',
    'PCI_PREF_LIMIT_UPPER32', 'PCI_PREF_MEMORY_BASE',
    'PCI_PREF_MEMORY_LIMIT', 'PCI_PREF_RANGE_MASK',
    'PCI_PREF_RANGE_TYPE_32', 'PCI_PREF_RANGE_TYPE_64',
    'PCI_PREF_RANGE_TYPE_MASK', 'PCI_PRIMARY_BUS',
    'PCI_PRI_ALLOC_REQ', 'PCI_PRI_CTRL', 'PCI_PRI_CTRL_ENABLE',
    'PCI_PRI_CTRL_RESET', 'PCI_PRI_MAX_REQ', 'PCI_PRI_STATUS',
    'PCI_PRI_STATUS_PASID', 'PCI_PRI_STATUS_RF',
    'PCI_PRI_STATUS_STOPPED', 'PCI_PRI_STATUS_UPRGI', 'PCI_PTM_CAP',
    'PCI_PTM_CAP_REQ', 'PCI_PTM_CAP_ROOT', 'PCI_PTM_CTRL',
    'PCI_PTM_CTRL_ENABLE', 'PCI_PTM_CTRL_ROOT',
    'PCI_PTM_GRANULARITY_MASK', 'PCI_PWR_CAP', 'PCI_PWR_DATA',
    'PCI_PWR_DSR', 'PCI_RCEC_BUSN', 'PCI_RCEC_BUSN_REG_VER',
    'PCI_RCEC_RCIEP_BITMAP', 'PCI_REBAR_CAP', 'PCI_REBAR_CAP_SIZES',
    'PCI_REBAR_CTRL', 'PCI_REBAR_CTRL_BAR_IDX',
    'PCI_REBAR_CTRL_BAR_SHIFT', 'PCI_REBAR_CTRL_BAR_SIZE',
    'PCI_REBAR_CTRL_NBAR_MASK', 'PCI_REBAR_CTRL_NBAR_SHIFT',
    'PCI_REVISION_ID', 'PCI_ROM_ADDRESS', 'PCI_ROM_ADDRESS1',
    'PCI_ROM_ADDRESS_ENABLE', 'PCI_ROM_ADDRESS_MASK', 'PCI_SATA_REGS',
    'PCI_SATA_REGS_INLINE', 'PCI_SATA_REGS_MASK',
    'PCI_SATA_SIZEOF_LONG', 'PCI_SATA_SIZEOF_SHORT',
    'PCI_SECONDARY_BUS', 'PCI_SEC_LATENCY_TIMER', 'PCI_SEC_STATUS',
    'PCI_SID_CHASSIS_NR', 'PCI_SID_ESR', 'PCI_SID_ESR_FIC',
    'PCI_SID_ESR_NSLOTS', 'PCI_SRIOV_BAR', 'PCI_SRIOV_CAP',
    'PCI_SRIOV_CAP_VFM', 'PCI_SRIOV_CTRL', 'PCI_SRIOV_CTRL_ARI',
    'PCI_SRIOV_CTRL_INTR', 'PCI_SRIOV_CTRL_MSE', 'PCI_SRIOV_CTRL_VFE',
    'PCI_SRIOV_CTRL_VFM', 'PCI_SRIOV_FUNC_LINK',
    'PCI_SRIOV_INITIAL_VF', 'PCI_SRIOV_NUM_BARS', 'PCI_SRIOV_NUM_VF',
    'PCI_SRIOV_STATUS', 'PCI_SRIOV_STATUS_VFM',
    'PCI_SRIOV_SUP_PGSIZE', 'PCI_SRIOV_SYS_PGSIZE',
    'PCI_SRIOV_TOTAL_VF', 'PCI_SRIOV_VFM', 'PCI_SRIOV_VFM_AV',
    'PCI_SRIOV_VFM_MI', 'PCI_SRIOV_VFM_MO', 'PCI_SRIOV_VFM_UA',
    'PCI_SRIOV_VF_DID', 'PCI_SRIOV_VF_OFFSET', 'PCI_SRIOV_VF_STRIDE',
    'PCI_SSVID_DEVICE_ID', 'PCI_SSVID_VENDOR_ID', 'PCI_STATUS',
    'PCI_STATUS_66MHZ', 'PCI_STATUS_CAP_LIST',
    'PCI_STATUS_DETECTED_PARITY', 'PCI_STATUS_DEVSEL_FAST',
    'PCI_STATUS_DEVSEL_MASK', 'PCI_STATUS_DEVSEL_MEDIUM',
    'PCI_STATUS_DEVSEL_SLOW', 'PCI_STATUS_FAST_BACK',
    'PCI_STATUS_IMM_READY', 'PCI_STATUS_INTERRUPT',
    'PCI_STATUS_PARITY', 'PCI_STATUS_REC_MASTER_ABORT',
    'PCI_STATUS_REC_TARGET_ABORT', 'PCI_STATUS_SIG_SYSTEM_ERROR',
    'PCI_STATUS_SIG_TARGET_ABORT', 'PCI_STATUS_UDF',
    'PCI_STD_HEADER_SIZEOF', 'PCI_STD_NUM_BARS',
    'PCI_SUBORDINATE_BUS', 'PCI_SUBSYSTEM_ID',
    'PCI_SUBSYSTEM_VENDOR_ID', 'PCI_TPH_BASE_SIZEOF', 'PCI_TPH_CAP',
    'PCI_TPH_CAP_LOC_MASK', 'PCI_TPH_CAP_ST_MASK',
    'PCI_TPH_CAP_ST_SHIFT', 'PCI_TPH_LOC_CAP', 'PCI_TPH_LOC_MSIX',
    'PCI_TPH_LOC_NONE', 'PCI_VC_CAP1_ARB_SIZE', 'PCI_VC_CAP1_EVCC',
    'PCI_VC_CAP1_LPEVCC', 'PCI_VC_CAP2_128_PHASE',
    'PCI_VC_CAP2_32_PHASE', 'PCI_VC_CAP2_64_PHASE',
    'PCI_VC_CAP2_ARB_OFF', 'PCI_VC_PORT_CAP1', 'PCI_VC_PORT_CAP2',
    'PCI_VC_PORT_CTRL', 'PCI_VC_PORT_CTRL_LOAD_TABLE',
    'PCI_VC_PORT_STATUS', 'PCI_VC_PORT_STATUS_TABLE',
    'PCI_VC_RES_CAP', 'PCI_VC_RES_CAP_128_PHASE',
    'PCI_VC_RES_CAP_128_PHASE_TB', 'PCI_VC_RES_CAP_256_PHASE',
    'PCI_VC_RES_CAP_32_PHASE', 'PCI_VC_RES_CAP_64_PHASE',
    'PCI_VC_RES_CAP_ARB_OFF', 'PCI_VC_RES_CTRL',
    'PCI_VC_RES_CTRL_ARB_SELECT', 'PCI_VC_RES_CTRL_ENABLE',
    'PCI_VC_RES_CTRL_ID', 'PCI_VC_RES_CTRL_LOAD_TABLE',
    'PCI_VC_RES_STATUS', 'PCI_VC_RES_STATUS_NEGO',
    'PCI_VC_RES_STATUS_TABLE', 'PCI_VENDOR_ID', 'PCI_VNDR_HEADER',
    'PCI_VPD_ADDR', 'PCI_VPD_ADDR_F', 'PCI_VPD_ADDR_MASK',
    'PCI_VPD_DATA', 'PCI_VSEC_HDR', 'PCI_VSEC_HDR_LEN_SHIFT',
    'PCI_X_BRIDGE_SSTATUS', 'PCI_X_BRIDGE_STATUS', 'PCI_X_CMD',
    'PCI_X_CMD_DPERR_E', 'PCI_X_CMD_ERO', 'PCI_X_CMD_MAX_READ',
    'PCI_X_CMD_MAX_SPLIT', 'PCI_X_CMD_READ_1K', 'PCI_X_CMD_READ_2K',
    'PCI_X_CMD_READ_4K', 'PCI_X_CMD_READ_512', 'PCI_X_CMD_SPLIT_1',
    'PCI_X_CMD_SPLIT_12', 'PCI_X_CMD_SPLIT_16', 'PCI_X_CMD_SPLIT_2',
    'PCI_X_CMD_SPLIT_3', 'PCI_X_CMD_SPLIT_32', 'PCI_X_CMD_SPLIT_4',
    'PCI_X_CMD_SPLIT_8', 'PCI_X_ECC_CSR', 'PCI_X_SSTATUS_133MHZ',
    'PCI_X_SSTATUS_266MHZ', 'PCI_X_SSTATUS_533MHZ',
    'PCI_X_SSTATUS_64BIT', 'PCI_X_SSTATUS_FREQ', 'PCI_X_SSTATUS_V1',
    'PCI_X_SSTATUS_V2', 'PCI_X_SSTATUS_VERS', 'PCI_X_STATUS',
    'PCI_X_STATUS_133MHZ', 'PCI_X_STATUS_266MHZ',
    'PCI_X_STATUS_533MHZ', 'PCI_X_STATUS_64BIT', 'PCI_X_STATUS_BUS',
    'PCI_X_STATUS_COMPLEX', 'PCI_X_STATUS_DEVFN',
    'PCI_X_STATUS_MAX_CUM', 'PCI_X_STATUS_MAX_READ',
    'PCI_X_STATUS_MAX_SPLIT', 'PCI_X_STATUS_SPL_DISC',
    'PCI_X_STATUS_SPL_ERR', 'PCI_X_STATUS_UNX_SPL',
    'VGA_ARB_RSRC_LEGACY_IO', 'VGA_ARB_RSRC_LEGACY_MEM',
    'VGA_ARB_RSRC_NONE', 'VGA_ARB_RSRC_NORMAL_IO',
    'VGA_ARB_RSRC_NORMAL_MEM', 'pci_device_cfg_read',
    'pci_device_cfg_read_u16', 'pci_device_cfg_read_u32',
    'pci_device_cfg_read_u8', 'pci_device_cfg_write',
    'pci_device_cfg_write_bits', 'pci_device_cfg_write_u16',
    'pci_device_cfg_write_u32', 'pci_device_cfg_write_u8',
    'pci_device_close_io', 'pci_device_enable',
    'pci_device_find_by_slot', 'pci_device_get_agp_info',
    'pci_device_get_bridge_buses', 'pci_device_get_bridge_info',
    'pci_device_get_device_name', 'pci_device_get_parent_bridge',
    'pci_device_get_pcmcia_bridge_info',
    'pci_device_get_subdevice_name', 'pci_device_get_subvendor_name',
    'pci_device_get_vendor_name', 'pci_device_has_kernel_driver',
    'pci_device_is_boot_vga', 'pci_device_map_legacy',
    'pci_device_map_memory_range', 'pci_device_map_range',
    'pci_device_map_region', 'pci_device_next', 'pci_device_open_io',
    'pci_device_probe', 'pci_device_read_rom',
    'pci_device_unmap_legacy', 'pci_device_unmap_memory_range',
    'pci_device_unmap_range', 'pci_device_unmap_region',
    'pci_device_vgaarb_decodes', 'pci_device_vgaarb_fini',
    'pci_device_vgaarb_get_info', 'pci_device_vgaarb_init',
    'pci_device_vgaarb_lock', 'pci_device_vgaarb_set_target',
    'pci_device_vgaarb_trylock', 'pci_device_vgaarb_unlock',
    'pci_get_strings', 'pci_id_match_iterator_create',
    'pci_io_read16', 'pci_io_read32', 'pci_io_read8',
    'pci_io_write16', 'pci_io_write32', 'pci_io_write8',
    'pci_iterator_destroy', 'pci_legacy_open_io',
    'pci_slot_match_iterator_create', 'pci_system_cleanup',
    'pci_system_init', 'pci_system_init_dev_mem', 'pciaddr_t',
    'struct_pci_agp_info', 'struct_pci_bridge_info',
    'struct_pci_device', 'struct_pci_device_iterator',
    'struct_pci_id_match', 'struct_pci_io_handle',
    'struct_pci_mem_region', 'struct_pci_pcmcia_bridge_info',
    'struct_pci_pcmcia_bridge_info_0',
    'struct_pci_pcmcia_bridge_info_1', 'struct_pci_slot_match',
    'uint16_t', 'uint32_t', 'uint8_t']
