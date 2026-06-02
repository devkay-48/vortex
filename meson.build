project('vortex', version: '1.0.0', license: 'GPL-3.0-or-later')

gnome = import('gnome')
python = import('python').find_installation('python3')

# GSettings schema
gnome.compile_schemas(
  depend_files: files('src/data/org.gnome.Vortex.gschema.xml')
)

install_data(
  'src/data/org.gnome.Vortex.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

# Desktop entry
install_data(
  'data/org.gnome.Vortex.desktop',
  install_dir: get_option('datadir') / 'applications'
)

# AppStream metadata
install_data(
  'data/org.gnome.Vortex.appdata.xml',
  install_dir: get_option('datadir') / 'metainfo'
)

# Icon
install_data(
  'data/icons/org.gnome.Vortex.svg',
  install_dir: get_option('datadir') / 'icons' / 'hicolor' / 'scalable' / 'apps'
)

# Python sources
install_subdir(
  'src',
  install_dir: get_option('datadir') / 'vortex',
  strip_directory: true
)

# Launcher script
configure_file(
  input: 'data/vortex.in',
  output: 'vortex',
  configuration: {'DATADIR': get_option('prefix') / get_option('datadir')},
  install: true,
  install_dir: get_option('bindir')
)
