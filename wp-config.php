<?php
/**
 * The base configurations of the WordPress.
 *
 * This file has the following configurations: MySQL settings, Table Prefix,
 * Secret Keys, WordPress Language, and ABSPATH. You can find more information
 * by visiting {@link http://codex.wordpress.org/Editing_wp-config.php Editing
 * wp-config.php} Codex page. You can get the MySQL settings from your web host.
 *
 * This file is used by the wp-config.php creation script during the
 * installation. You don't have to use the web site, you can just copy this file
 * to "wp-config.php" and fill in the values.
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'ahajari_wrdp1');

/** MySQL database username */
define('DB_USER', 'ahajari_wrdp1');

/** MySQL database password */
define('DB_PASSWORD', 'g6TmCBnybZn4BEEW');

/** MySQL hostname */
define('DB_HOST', 'localhost');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define('AUTH_KEY',         'RSpCl6HesquFBrEwNJ(XOAW1=;rORtiQ8Ao$GYv_H:htCJSF8mPPV-r$AAHquT<EwnP(<x');
define('SECURE_AUTH_KEY',  'XOekxn)vn(n>DxuE\`XLn@UV6B:bH>e8ppltqsF2oK(uMo$L?S|rl$QNAuYcBm^H!hJ*SpWU~B5j');
define('LOGGED_IN_KEY',    '5yN4MSGf8b!AJHLKhRtHY)Mci|>O\`^I~QL4-Fq)ou54D>(B#Vkzu<8(hHX-70QQDRaf1(tT4');
define('NONCE_KEY',        'KmXCn1$3*H!H=ovPa9QVIGeDgxk4*Vye*PN*QlEcrG|J6p6_R/5xeoLzS!uB^Dv>2if4');
define('AUTH_SALT',        '-iR$zL|=OmmvJtG_R~2zCSP@y8Yjj11Dl#!o3^WI8P/okD>WK=MmcPfqR6i:\`|Lq');
define('SECURE_AUTH_SALT', 'jYN=LkoRz>n$ay2FfA^RH@1Tjym2uNkC(_p^*N)CkY11FB\`*Adm=t2c\`OpF8kbV4OTdfL');
define('LOGGED_IN_SALT',   'CPNkw/^zd>/Q*DO$aoI3hu9phby*s5Ol3I#i$eL4A$hHp_IGTe^2-$m*QEb7=9vgV:>rS#\`XouQ');
define('NONCE_SALT',       'kL1vJ-h6DEYmyvPvJ2qYnFC#m^KkzFzCX-|7Q($->?:l\`?M4vfueAWc=gqrg:');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each a unique
 * prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * WordPress Localized Language, defaults to English.
 *
 * Change this to localize WordPress. A corresponding MO file for the chosen
 * language must be installed to wp-content/languages. For example, install
 * de_DE.mo to wp-content/languages and set WPLANG to 'de_DE' to enable German
 * language support.
 */
define('WPLANG', '');

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 */
define('WP_DEBUG', false);
define('WP_DEBUG_LOG', false);
define('WP_DEBUG_DISPLAY', false);

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
