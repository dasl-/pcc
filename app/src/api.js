import axios from 'axios';

class APIClient {

  constructor(receivers) {
    this.clients = {};
    receivers.forEach(function (receiver, index) {
      this.clients[receiver] = axios.create({
        baseURL: "//" + receiver + ':8080',
        json: true
      });
    }.bind(this));
  }

  getReceiverData(receiver) {
    return this.perform(receiver, 'get', '/receiver_data');
  }

  setVolPct(receiver, vol_pct, set_airplay_client_vol) {
    return this.perform(receiver, 'post', '/vol_pct', {
      vol_pct: vol_pct,
      set_airplay_client_vol: set_airplay_client_vol
    });
  }

  async perform (receiver, method, resource, data) {
    return this.clients[receiver]({
       method,
       url: resource,
       data,
       headers: {}
     }).then(resp => {
       return resp.data ? resp.data : [];
     })
  }
}

export default APIClient;
