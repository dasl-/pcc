import React from 'react';
import APIClient from 'api';

import config from 'config.json';

import './app.css';
import Receiver from '../receiver/receiver';

class App extends React.Component {

  static RECEIVER_POLL_INTERVAL_MS = 1000;

  constructor(props) {
    super(props);

    var receivers = {};
    config.receivers.forEach(function (receiver, index) {
      receivers[receiver] = {};
      receivers[receiver]['is_poll_in_progress'] = false;
      receivers[receiver]['vol_pct'] = undefined;
    });

    this.state = {
      receivers: receivers
    };

    this.apiClient = new APIClient(config.receivers);
    this.setVolPct = this.setVolPct.bind(this);
    this.makeBtDiscoverable = this.makeBtDiscoverable.bind(this);
    this.disconnectClients = this.disconnectClients.bind(this);
    this.receiver_poll_timeout = {};
  }

  componentDidMount() {
    for (var receiver in this.state.receivers) {
      this.getReceiverData(receiver);
    }
  }

  render() {
    return (
      <div className='h-100 bg-primary bg-background'>
        <div className={"container-fluid app-body"}>
          <h1>Pi Control Center</h1>
          {Object.keys(this.state.receivers).map(function(receiver, index) {
            return <Receiver
              key = {index}
              receiver = {receiver}
              hostname = {this.state.receivers[receiver]['hostname']}
              vol_pct = {this.state.receivers[receiver]['vol_pct']}
              setVolPct = {this.setVolPct}
              makeBtDiscoverable = {this.makeBtDiscoverable}
              bt_discoverable = {this.state.receivers[receiver]['bt_discoverable']}
              disconnectClients = {this.disconnectClients}
            />
          }.bind(this))}
        </div>
      </div>
    );
  }

  setVolPct(receiver, vol_pct, set_airplay_client_vol = false) {
    return this.apiClient.setVolPct(receiver, vol_pct, set_airplay_client_vol)
  }

  makeBtDiscoverable(receiver) {
    return this.apiClient.makeBtDiscoverable(receiver);
  }

  disconnectClients(receiver) {
    return this.apiClient.disconnectClients(receiver);
  }

  cancelReceiverPoll(receiver) {
    if (receiver in this.receiver_poll_timeout) {
      clearTimeout(this.receiver_poll_timeout[receiver]);
    }
  }

  getReceiverData(receiver) {
    if (this.state.receivers[receiver]['is_poll_in_progress']) {
      this.cancelReceiverPoll(receiver);
      this.receiver_poll_timeout[receiver] = setTimeout(this.getReceiverData.bind(this, receiver), App.RECEIVER_POLL_INTERVAL_MS);
      return;
    }


    var new_receivers = this.cloneReceivers();
    new_receivers[receiver]['is_poll_in_progress'] = true;
    this.setState({receivers: new_receivers});

    var response = null;
    return this.apiClient
      .getReceiverData(receiver)
      .then((data) => {
        if (data.success) {
          data.vol_pct = +(data.vol_pct.toFixed(0));
          response = data;
        }
      })
      .finally(() => {
        this.receiver_poll_timeout[receiver] = setTimeout(this.getReceiverData.bind(this, receiver), App.RECEIVER_POLL_INTERVAL_MS);

        var new_receivers = this.cloneReceivers()
        if (response.success) {
          new_receivers[receiver]['vol_pct'] = response.vol_pct;
          new_receivers[receiver]['hostname'] = response.hostname;
          new_receivers[receiver]['bt_discoverable'] = response.bt_discoverable;
        }
        new_receivers[receiver]['is_poll_in_progress'] = false;
        this.setState({receivers: new_receivers});
      });
  }

  cloneReceivers() {
    var new_receivers = { ...this.state.receivers }
    for (var receiver in new_receivers) {
      new_receivers[receiver] = { ...new_receivers[receiver] }
    }
    return new_receivers;
  }

}

export default App;
