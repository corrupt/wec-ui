# WEC UI

 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

wec-ui is a simple user interface for instrumenting [Website Evidence Collector](https://github.com/EU-EDPS/website-evidence-collector) with a very specific workflow.
* Create a browser profile with certain settings for a given website applied (like tracking banners configured, cookies set, etc..) by starting a browser and giving the user the possibility to interact with the site.
* Starting WEC with the newly created browser profile

<img width="1115" alt="image" src="https://user-images.githubusercontent.com/365169/192270522-e4c714b6-fd64-4344-9d1f-1905fec5e077.png">

wec-ui requires a configuration file in `$XDG_CONFIG_HOME/wecui/config.cfg`, usually `${HOME}/.config/wecui/config.cfg`. An example config file is provided. This is necessary to point wec-ui to a installation directory of WEC.
