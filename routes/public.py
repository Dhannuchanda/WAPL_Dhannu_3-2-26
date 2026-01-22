from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from database import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/verify-certificate/<cert_id>', methods=['GET'])
def verify_certificate(cert_id):
    try:
        # Get certificate
        certificate = db.execute_query(
            '''SELECT c.*, s.full_name, s.wapl_id, d.domain_name
               FROM certificates c
               LEFT JOIN students s ON c.student_id = s.id
               LEFT JOIN domains d ON s.domain_id = d.id
               WHERE c.certificate_unique_id = ?''',
            (cert_id,),
            fetch_one=True
        )
        
        if not certificate:
            return render_template('verify_certificate.html', 
                                 valid=False, 
                                 message='Certificate not found')
        
        cert_dict = dict(certificate)
        is_expired = datetime.fromisoformat(cert_dict['expiry_date']) < datetime.now()
        is_active = cert_dict['is_active'] == 1
        
        if not is_active:
            return render_template('verify_certificate.html',
                                 valid=False,
                                 message='Certificate has been revoked')
        
        if is_expired:
            return render_template('verify_certificate.html',
                                 valid=False,
                                 message='Certificate has expired',
                                 certificate=cert_dict)
        
        return render_template('verify_certificate.html',
                             valid=True,
                             certificate=cert_dict)
        
    except Exception as e:
        return render_template('verify_certificate.html',
                             valid=False,
                             message=f'Error: {str(e)}')

@public_bp.route('/api/verify-certificate/<cert_id>', methods=['GET'])
def verify_certificate_api(cert_id):
    try:
        certificate = db.execute_query(
            '''SELECT c.*, s.full_name, s.wapl_id, d.domain_name
               FROM certificates c
               LEFT JOIN students s ON c.student_id = s.id
               LEFT JOIN domains d ON s.domain_id = d.id
               WHERE c.certificate_unique_id = ?''',
            (cert_id,),
            fetch_one=True
        )
        
        if not certificate:
            return jsonify({'valid': False, 'message': 'Certificate not found'}), 404
        
        cert_dict = dict(certificate)
        is_expired = datetime.fromisoformat(cert_dict['expiry_date']) < datetime.now()
        is_active = cert_dict['is_active'] == 1
        
        if not is_active:
            return jsonify({'valid': False, 'message': 'Certificate has been revoked'}), 400
        
        return jsonify({
            'valid': not is_expired,
            'expired': is_expired,
            'certificate': cert_dict
        }), 200
        
    except Exception as e:
        return jsonify({'valid': False, 'message': str(e)}), 500
