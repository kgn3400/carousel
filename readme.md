<!-- markdownlint-disable MD041 -->
![GitHub release (latest by date)](https://img.shields.io/github/v/release/kgn3400/carousel)
![GitHub all releases](https://img.shields.io/github/downloads/kgn3400/carousel/total)
![GitHub last commit](https://img.shields.io/github/last-commit/kgn3400/carousel)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kgn3400/carousel)
[![Validate% with hassfest](https://github.com/kgn3400/carousel/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/kgn3400/carousel/actions/workflows/hassfest.yaml)

<img align="left" width="80" height="80" src="https://kgn3400.github.io/carousel/assets/icon.png" alt="App icon">

# Carousel

<br/>
The Carousel integration helper allows you to create a binary_sensor or sensor which rotate through a set of the same type of entities in the same card, with a user defined time interval. if the binary_sensors/sensors set has the same attribute, it's possible to use cards which support showing attributes.

<br/>
<br/>

<img src="https://kgn3400.github.io/carousel/assets/carousel_video.png" width="400" height="auto" alt="Carousel video">

<br/>
<br/>

For installation instructions until the Carousel helper is part of HACS, [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
Or click [![My Home Assistant](https://img.shields.io/badge/Home%20Assistant-%2341BDF5.svg?style=flat&logo=home-assistant&label=Add%20to%20HACS)](https://my.home-assistant.io/redirect/hacs_repository/?owner=kgn3400&repository=carousel&category=integration)

---

## Configuration

Configuration is setup via UI in Home assistant. To add one, go to [Settings > Devices & Services > Helpers](https://my.home-assistant.io/redirect/helpers) and click the add button. Next choose the [Carousel helper](https://my.home-assistant.io/redirect/config_flow_start?domain=carousel) option.
Or click
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=carousel)

<!-- <img src="images/config.png" width="400" height="auto" alt="Config"> -->
<img src="https://kgn3400.github.io/carousel/assets/config.png" width="400" height="auto" alt="Config">
<br/>
<br/>

It's possible to synchronize the rotation between multiple carousels by using the same optional Timer helper. Restarting the Timer helper can be done via the Carousel helper or via an automation

The optional 'show if template' config settings is used to decide if the entity should be shown. The evaluated result should return True for the entity to be included in carousel rotation. Template values = state and dict state_attributes.
If there is no entities to show, then the Carousel entity state will be set to unknown. And the state can be used in the conditional card to decide if the card should be shown.

---

## Actions

Available actions: __add__, __remove__, __show_entity__, __show_next__ and __show_prev__

### Action carousel.binary_sensor_add/carousel.sensor_add

Add entity to Carousel helper.

### Action carousel.binary_sensor_remove/carousel.sensor_remove

Remove entity from Carousel helper.

### Action carousel.binary_sensor_show_next/carousel.sensor_show_next

Show next entity in Carousel helper.

### Action carousel.binary_sensor_show_prev/carousel.sensor_show_prev

Show previous ext entity in Carousel helper.

## Automation triggers

### Carousel starting over

Trigger fired when the carousel starting over with the first entity in the set.
