import React from 'react';
import './receiver.css';

import App from '../app/app';

import 'rc-slider/assets/index.css';
import Slider from 'rc-slider';

class Receiver extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      vol_pct: this.props.vol_pct,
      is_vol_locked: false,
      is_vol_lock_releasable: true,
      vol_lock_marked_releasable_time: 0,
    };
  }

  render() {
    var bluetooth_class = (this.props.bt_discoverable ? 'bt-discoverable' : 'bt-not-discoverable') + ' bi bi-bluetooth receiver-icon';
    var connected_client_elements = '';
    if (this.props.connected_client_name) {
      connected_client_elements = "<span className='glyphicon glyphicon-link receiver-icon' aria-hidden='true' /> " + this.props.connected_client_name;
    }
    return (
      <div className='receiver'>
        <h6>
          {this.props.hostname}
          <svg onClick={this.handleBluetoothClick} xmlns="http://www.w3.org/2000/svg" fill="currentColor" className={bluetooth_class} viewBox="0 0 16 16"><path fillRule="evenodd" d="m8.543 3.948 1.316 1.316L8.543 6.58V3.948Zm0 8.104 1.316-1.316L8.543 9.42v2.632Zm-1.41-4.043L4.275 5.133l.827-.827L7.377 6.58V1.128l4.137 4.136L8.787 8.01l2.745 2.745-4.136 4.137V9.42l-2.294 2.274-.827-.827L7.133 8.01ZM7.903 16c3.498 0 5.904-1.655 5.904-8.01 0-6.335-2.406-7.99-5.903-7.99C4.407 0 2 1.655 2 8.01 2 14.344 4.407 16 7.904 16Z"/></svg>
          <span onClick={this.handleDisconnectClick} style={{color: "#d94848"}} className='glyphicon glyphicon-remove receiver-icon' aria-hidden='true' />
          {connected_client_elements}
         </h6>
        <div className='row'>
          <div className='col-1 p-0 text-right'><span className='glyphicon glyphicon-volume-down bg-light-text vol-icon' aria-hidden='true' /></div>
          <div className='col-10 volume-container'>
            <Slider
              className='volume'
              min={0}
              max={100}
              step={1}
              onBeforeChange={this.grabVolMutex}
              onChange={this.onVolChange}
              onAfterChange={this.markVolMutexReleasable}
              value={this.state.is_vol_locked ? this.state.vol_pct : this.props.vol_pct}
            />
          </div>
          <div className='col-1 p-0'><span className='glyphicon glyphicon-volume-up bg-light-text vol-icon' aria-hidden='true' /></div>
        </div>
      </div>
    );
  }

  handleBluetoothClick = () => {
    if (this.props.bt_discoverable) {
      return;
    }
    this.props.makeBtDiscoverable(this.props.receiver)
  };

  handleDisconnectClick = () => {
    this.props.disconnectClients(this.props.receiver)
  };

  onVolChange = (vol_pct) => {
    this.props.setVolPct(this.props.receiver, vol_pct)
    this.setState({vol_pct: vol_pct});
  };

  grabVolMutex = () => {
    this.setState({
      is_vol_locked: true,
      is_vol_lock_releasable: false
    });
  };
  markVolMutexReleasable = (vol_pct) => {
    // Set airplay client volume after slider movement has finished, because sending the airplay dbus command
    // has variable latency. If we set it with every change event, we would often see some volume
    // changes happen out of order due to race conditions, resulting in bad UI.
    this.props.setVolPct(this.props.receiver, vol_pct, true)

    this.setState({
      is_vol_lock_releasable: true,
      vol_lock_marked_releasable_time: (new Date()).getTime()
    });
  };
  releaseVolMutex = () => {
    this.setState({
      is_vol_locked: false,
      is_vol_lock_releasable: true
    });
  };

  // TODO: this is deprecated
  componentWillReceiveProps(nextProps) {
    if (this.state.is_vol_locked && this.state.is_vol_lock_releasable) {
      var millis_since_vol_locked_marked_releasable = (new Date()).getTime() - this.state.vol_lock_marked_releasable_time;
      if (millis_since_vol_locked_marked_releasable > (App.RECEIVER_POLL_INTERVAL_MS + 500)) {
        this.releaseVolMutex();
      }
    }

    if (!this.state.is_vol_locked) {
      this.setState({vol_pct: nextProps.vol_pct});
    }
  }

}

export default Receiver;
