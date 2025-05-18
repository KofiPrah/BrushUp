import React, { useState } from 'react';
import { toast } from 'react-toastify';
import useCritiqueActions from '../hooks/useCritiqueActions';

const CritiqueModeration = ({ critique, onSuccess, isArtworkOwner }) => {
  const [showHideModal, setShowHideModal] = useState(false);
  const [showUnhideModal, setShowUnhideModal] = useState(false);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [showFlagModal, setShowFlagModal] = useState(false);
  const [reason, setReason] = useState('');
  const [replyText, setReplyText] = useState('');
  
  const { 
    loading, 
    error, 
    success,
    hideCritique, 
    unhideCritique, 
    flagCritique, 
    replyCritique 
  } = useCritiqueActions();
  
  // Handle hide critique
  const handleHideSubmit = async (e) => {
    e.preventDefault();
    try {
      await hideCritique(critique.id, reason);
      toast.success('Critique has been hidden successfully');
      setShowHideModal(false);
      setReason('');
      if (onSuccess) onSuccess();
    } catch (err) {
      toast.error(error || 'An error occurred while hiding the critique');
    }
  };
  
  // Handle unhide critique
  const handleUnhideSubmit = async (e) => {
    e.preventDefault();
    try {
      await unhideCritique(critique.id);
      toast.success('Critique has been unhidden successfully');
      setShowUnhideModal(false);
      if (onSuccess) onSuccess();
    } catch (err) {
      toast.error(error || 'An error occurred while unhiding the critique');
    }
  };
  
  // Handle flag critique
  const handleFlagSubmit = async (e) => {
    e.preventDefault();
    try {
      await flagCritique(critique.id, reason);
      toast.success('Critique has been flagged successfully');
      setShowFlagModal(false);
      setReason('');
      if (onSuccess) onSuccess();
    } catch (err) {
      toast.error(error || 'An error occurred while flagging the critique');
    }
  };
  
  // Handle reply to critique
  const handleReplySubmit = async (e) => {
    e.preventDefault();
    try {
      await replyCritique(critique.id, replyText);
      toast.success('Your reply has been added successfully');
      setShowReplyModal(false);
      setReplyText('');
      if (onSuccess) onSuccess();
    } catch (err) {
      toast.error(error || 'An error occurred while adding your reply');
    }
  };
  
  return (
    <div className="critique-moderation mt-2">
      {isArtworkOwner && (
        <>
          {!critique.is_hidden ? (
            <button
              type="button"
              className="btn btn-sm btn-outline-danger me-2"
              onClick={() => setShowHideModal(true)}
            >
              <i className="bi bi-eye-slash"></i> Hide
            </button>
          ) : (
            <button
              type="button"
              className="btn btn-sm btn-outline-success me-2"
              onClick={() => setShowUnhideModal(true)}
            >
              <i className="bi bi-eye"></i> Unhide
            </button>
          )}
          
          <button
            type="button"
            className="btn btn-sm btn-outline-primary"
            onClick={() => setShowReplyModal(true)}
          >
            <i className="bi bi-reply"></i> Reply
          </button>
        </>
      )}
      
      {!isArtworkOwner && (
        <button
          type="button"
          className="btn btn-sm btn-outline-warning"
          onClick={() => setShowFlagModal(true)}
        >
          <i className="bi bi-flag"></i> Flag
        </button>
      )}
      
      {/* Hide Modal */}
      {showHideModal && (
        <div className="modal d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Hide Critique</h5>
                <button type="button" className="btn-close" onClick={() => setShowHideModal(false)}></button>
              </div>
              <form onSubmit={handleHideSubmit}>
                <div className="modal-body">
                  <p>Are you sure you want to hide this critique? It will only be visible to you and the critique author.</p>
                  <div className="form-group">
                    <label htmlFor="hideReason">Reason (optional):</label>
                    <textarea
                      className="form-control"
                      id="hideReason"
                      rows="3"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowHideModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-danger" disabled={loading}>
                    {loading ? 'Processing...' : 'Hide Critique'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Unhide Modal */}
      {showUnhideModal && (
        <div className="modal d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Unhide Critique</h5>
                <button type="button" className="btn-close" onClick={() => setShowUnhideModal(false)}></button>
              </div>
              <form onSubmit={handleUnhideSubmit}>
                <div className="modal-body">
                  <p>Are you sure you want to unhide this critique? It will become visible to everyone.</p>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowUnhideModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-success" disabled={loading}>
                    {loading ? 'Processing...' : 'Unhide Critique'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Reply Modal */}
      {showReplyModal && (
        <div className="modal d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Reply to Critique</h5>
                <button type="button" className="btn-close" onClick={() => setShowReplyModal(false)}></button>
              </div>
              <form onSubmit={handleReplySubmit}>
                <div className="modal-body">
                  <div className="form-group">
                    <label htmlFor="replyText">Your Reply:</label>
                    <textarea
                      className="form-control"
                      id="replyText"
                      rows="4"
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      required
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowReplyModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary" disabled={loading || !replyText.trim()}>
                    {loading ? 'Sending...' : 'Submit Reply'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      
      {/* Flag Modal */}
      {showFlagModal && (
        <div className="modal d-block" tabIndex="-1" role="dialog">
          <div className="modal-dialog" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Flag Inappropriate Critique</h5>
                <button type="button" className="btn-close" onClick={() => setShowFlagModal(false)}></button>
              </div>
              <form onSubmit={handleFlagSubmit}>
                <div className="modal-body">
                  <p>Please provide a reason for flagging this critique:</p>
                  <div className="form-group">
                    <label htmlFor="flagReason">Reason:</label>
                    <textarea
                      className="form-control"
                      id="flagReason"
                      rows="3"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      required
                    ></textarea>
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowFlagModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-warning" disabled={loading || !reason.trim()}>
                    {loading ? 'Processing...' : 'Flag Critique'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CritiqueModeration;