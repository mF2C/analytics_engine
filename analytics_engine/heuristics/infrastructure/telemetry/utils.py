import re

EXP_INST_PATTERN = r'exported_instance:+?[A-Za-z0-9-]+;'
LIBVIRT_TAP_PATTERN = r'libvirt:tap+?[A-Za-z0-9-]+;'
LIBVIRT_TAP_REPL_TXT = 'libvirt:tap_'

def clean_vm_telemetry_colnames(names):
    sep = '###'
    names_str = sep.join(names)
    names_str = re.sub(EXP_INST_PATTERN, '', names_str)
    counter = 0
    taps_set= set(re.findall(LIBVIRT_TAP_PATTERN, names_str))
    for i, tap in enumerate(taps_set):
        names_str = names_str.replace(tap, LIBVIRT_TAP_REPL_TXT+str(i)+';')
    return names_str.split(sep)

