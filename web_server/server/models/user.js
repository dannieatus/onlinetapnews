var bcrypt = require('bcrypt');
var mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  email: {
    type: String,
    index: { unique: true }
  },
  password: String,
});


UserSchema.methods.comparePassword = function comparePassword(password, callback) {
  bcrypt.compare(password, this.password, callback);
}

UserSchema.pre('save', function saveHook(next) {
  const user = this;

  if (!user.isModified('password')) return next();

  return bcrypt.genSalt((saltError, salt) => {
    // if salterror
    if (saltError) { 
      return next(saltError); 
    }
    //if salt
    return bcrypt.hash(user.password, salt, (hashError, hash) => {
      //if hasherror
      if (hashError) { 
        return next(hashError); 
      }
      // replace the plain password with the hashed one.
      user.password = hash;
      return next();
    });
  });
});

module.exports = mongoose.model('User', UserSchema);