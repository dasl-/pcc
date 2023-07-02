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
              vol_pct = {this.state.receivers[receiver]['vol_pct']}
              setVolPct = {this.setVolPct}
            />
          }.bind(this))}
        </div>
      </div>
    );
  }

  setVolPct(receiver, vol_pct) {
    return this.apiClient.setVolPct(receiver, vol_pct)
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

    var vol_pct = null;
    return this.apiClient
      .getReceiverData(receiver)
      .then((data) => {
        if (data.success) {
          vol_pct = +(data.vol_pct.toFixed(0));
        }
      })
      .finally((data) => {
        this.receiver_poll_timeout[receiver] = setTimeout(this.getReceiverData.bind(this, receiver), App.RECEIVER_POLL_INTERVAL_MS);

        var new_receivers = this.cloneReceivers()
        if (vol_pct !== null) {
          new_receivers[receiver]['vol_pct'] = vol_pct;
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
