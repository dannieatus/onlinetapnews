import 'materialize-css/dist/css/materialize.min.css';
import 'materialize-css/dist/js/materialize.min.js';
import './App.css';

//import NewsPanel from '../NewsPanel/NewsPanel';
import React from 'react';
import logo from './logo.png';
import NewsPanel from '../NewsPanel/NewsPanel';
//because line 8 has class, so html limiande class has to changed to classname
//materinalze's container style
// here only need to include newspanel
class App extends React.Component {
	render() {
		return(
			<div>
				<img className='logo' src={logo} alt='logo' />
				<div className='container'>
					<NewsPanel />
				</div>
			</div>
		);
	}
}
// for let someone who call this app can see, not export others cannot see
export default App;