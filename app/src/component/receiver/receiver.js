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
      vol_lock_marked_releasable_time: 0
    };
  }

  render() {
    return (
      <div className='receiver'>
        <h6>{this.props.hostname}</h6>
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
  markVolMutexReleasable = () => {
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