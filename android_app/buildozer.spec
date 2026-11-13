[app]

title = JOMZ Tracker PRO
package.name = jomztrackerpro
package.domain = org.jomz

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas

version = 1.0.0
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 23
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2

[buildozer]

log_level = 2
warn_on_root = 1
